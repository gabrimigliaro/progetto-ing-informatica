import asyncio

import log
from data import InData, InDataLogin, InUpdateData, OutDataLogin, OutUpdateData
import state
from state import connectedAps, inQueue, knownWatches, outQueue, lastSeen, watchdogAlerted
import time

WATCHDOG_TIMEOUT = 20.0
WATCHDOG_CHECK_INTERVAL = 5.0


async def writeLine(writer, line: str):
    try:
        writer.write((line.strip() + "\n").encode("utf-8"))
        await writer.drain()
        return True
    except Exception as e:
        log.stampaWarning(f"Invio all'ESP32 fallito: {e}")
        return False


async def sendToAp(line: str):
    await outQueue.put(line)


async def outLoop():
    while True:
        line = await outQueue.get()
        try:
            aps = list(connectedAps.values())
            if not aps:
                log.stampaWarning(f"TX broadcast: nessun ESP32 connesso, riga persa: {line}")
                continue
            log.stampaInfo(f"TX broadcast ({len(aps)} AP): {line}")

            tasks = [writeLine(d["writer"], line) for d in aps]
            await asyncio.gather(*tasks)
        except Exception as e:
            log.stampaAllarme(f"Errore nell'invio di '{line}': {e}")
        finally:
            outQueue.task_done()


async def sendToWebsocket(line: str):
    ws = state.wsConn
    if ws is None:
        log.stampaWarning(f"WS TX: Web UI non connessa, messaggio scartato: {line}")
        return
    try:
        await ws.send(line)
    except Exception as e:
        log.stampaWarning(f"WS TX: invio fallito ({e}), messaggio perso: {line}")

def aggiornaWatchdog(uid: int):
    lastSeen[uid] = time.monotonic()
    if uid in watchdogAlerted:
        watchdogAlerted.remove(uid)
        log.stampaInfo(f"WATCHDOG: orologio uid={uid} tornato attivo")


async def watchdogLoop():
    log.stampaInfo(f"WATCHDOG: avviato (timeout={WATCHDOG_TIMEOUT}s, check={WATCHDOG_CHECK_INTERVAL}s)")
    while True:
        await asyncio.sleep(WATCHDOG_CHECK_INTERVAL)
        now = time.monotonic()

        for uid in set(knownWatches.values()):
            if uid not in lastSeen:
                lastSeen[uid] = now

        for uid, ultimoContatto in list(lastSeen.items()):
            if (now - ultimoContatto) > WATCHDOG_TIMEOUT and uid not in watchdogAlerted:
                watchdogAlerted.add(uid)
                log.stampaWarning(
                    f"WATCHDOG: nessun pacchetto da uid={uid} per oltre {WATCHDOG_TIMEOUT}s -> WS 20,{uid}"
                )
                await sendToWebsocket(f"20,{uid}")
        
async def watchdogLoop():
    log.stampaInfo(f"WATCHDOG: avviato (timeout={WATCHDOG_TIMEOUT}s, check={WATCHDOG_CHECK_INTERVAL}s)")
    while True:
        try:
            await asyncio.sleep(WATCHDOG_CHECK_INTERVAL)
            now = time.monotonic()

            for uid in set(knownWatches.values()):
                if uid not in lastSeen:
                    lastSeen[uid] = now

            for uid, ultimoContatto in list(lastSeen.items()):
                if (now - ultimoContatto) > WATCHDOG_TIMEOUT and uid not in watchdogAlerted:
                    watchdogAlerted.add(uid)
                    log.stampaWarning(
                        f"WATCHDOG: nessun pacchetto da uid={uid} per oltre {WATCHDOG_TIMEOUT}s -> WS 20,{uid}"
                    )
                    await sendToWebsocket(f"20,{uid}")
        except Exception as e:
            log.stampaAllarme(f"WATCHDOG: errore nel loop: {e}")


async def manageUpdate(packet):
    # Da fare
    return None


async def routePacket(packet):
    if isinstance(packet, InDataLogin):
        uid = knownWatches.get(packet.mac)
        if uid is not None:
            aggiornaWatchdog(uid)
            log.stampaInfo(f"LOGIN {packet.mac} noto (uid={uid}) via {packet.apName} -> risposta")
            response = OutDataLogin(pid=1, mac=packet.mac, uid=uid)
            await sendToAp(response.toLine())
        else:
            log.stampaInfo(f"LOGIN {packet.mac} nuovo via {packet.apName} -> WS")
            line = f"0,{packet.apName},{packet.mac}"
            await sendToWebsocket(line)

    elif isinstance(packet, InData):
        aggiornaWatchdog(packet.uid)
        msg = (
            f"DATA uid={packet.uid} bpm={packet.bpm} bat={packet.battery} "
            f"em={packet.emergency} fall={packet.fall} via {packet.apName} "
            f"({packet.rssi}) -> WS"
        )
        if packet.emergency or packet.fall:
            log.stampaWarning(msg)
        else:
            log.stampaInfo(msg)
        line = (
            f"10,{packet.apName},{packet.uid},{packet.bpm},{packet.battery},"
            f"{packet.steps},{packet.emergency},{packet.fall},{packet.rssi}"
        )
        await sendToWebsocket(line)

    elif isinstance(packet, InUpdateData):
        aggiornaWatchdog(packet.uid)
        line = await manageUpdate(packet)
        if line:
            log.stampaInfo(f"UPDATE uid={packet.uid} via {packet.apName} -> risposta")
            await sendToAp(line)
        else:
            log.stampaInfo(f"UPDATE uid={packet.uid} via {packet.apName} -> nessuna risposta")


async def routeLoop():
    while True:
        packet = await inQueue.get()
        try:
            await routePacket(packet)
        except Exception as e:
            log.stampaAllarme(f"Errore nello smistamento di {packet}: {e}")
        finally:
            inQueue.task_done()