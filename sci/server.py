import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosed

import log
from data import InData, InDataLogin, InUpdateData, OutDataLogin
from deduplicator import processPacket
from router import sendToAp
import state
from state import connectedAps, knownWatches
from storage import saveKnownWatches

WS_SERVER_URL = "wss://rsa-monitoring.gmigliaro.it/api/ws"


# --- TCP SERVER (Nodi ESP) ---
# Formato righe: apName|t<PID>,campi...
#   AP1|t0,AA:BB:CC:DD:EE:FF,rssi
#   AP1|t10,uid,bpm,battery,steps,emergency,fall,rssi
#   AP1|t2,uid,rssi

def parseLine(raw: bytes):
    line = raw.decode("utf-8").strip()
    if not line:
        return None

    if "|t" not in line:
        raise ValueError("formato atteso 'apName|t<PID>,...'")

    apName, rest = line.split("|t", 1)
    if not apName:
        raise ValueError("formato atteso 'apName|t<PID>,...'")

    fields = rest.split(",")
    pid = int(fields[0])
    a = fields[1:]

    if pid == 0 and len(a) == 1:
        mac = a[0].strip().upper()
        if len(mac) != 17:
            raise ValueError(f"MAC non valido: {mac[:30]}")
        return apName, InDataLogin(pid=0, apName=apName, mac=mac)

    if pid == 10 and len(a) == 7:
        return apName, InData(
            pid=10,
            apName=apName,
            uid=int(a[0]),
            bpm=int(a[1]),
            battery=int(a[2]),
            steps=int(a[3]),
            emergency=int(a[4]),
            fall=int(a[5]),
            rssi=int(a[6]),
        )

    if pid == 2 and len(a) == 1:
        return apName, InUpdateData(pid=2, apName=apName, uid=int(a[0]))

    log.stampaWarning(f"RX {apName}: pacchetto t{pid} sconosciuto o incompleto: {line[:120]}")
    return apName, None


def describe(packet):
    if isinstance(packet, InDataLogin):
        return f"mac={packet.mac}"
    if isinstance(packet, InData):
        return f"uid={packet.uid} bpm={packet.bpm} em={packet.emergency} fall={packet.fall}"
    return f"uid={packet.uid}"


async def ManTCPClient(reader, writer):
    apName = None
    peername = writer.get_extra_info("peername")
    clientIp = peername[0] if peername else "Unknown"
    log.stampaInfo(f"TCP: connessione da {clientIp}")

    try:
        while True:
            lineBytes = await reader.readline()
            if not lineBytes:
                break

            try:
                parsed = parseLine(lineBytes)
            except (UnicodeDecodeError, ValueError, IndexError) as e:
                log.stampaWarning(f"RX {clientIp}: riga malformata {lineBytes[:120]} ({e})")
                continue

            if parsed is None:
                continue

            name, packet = parsed
            if apName is None:
                apName = name
                connectedAps[apName] = {"writer": writer, "ip": clientIp}
                log.stampaInfo(f"TCP: AP '{apName}' registrato ({clientIp})")
            elif name != apName:
                log.stampaWarning(f"RX {apName}: riga con nome diverso '{name}' scartata")
                continue

            if packet is not None:
                log.stampaInfo(f"RX {apName} t{packet.pid} {describe(packet)}")
                processPacket(packet)

    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    except Exception as e:
        log.stampaAllarme(f"TCP {clientIp}: {e}")
    finally:
        if apName and connectedAps.get(apName, {}).get("writer") is writer:
            del connectedAps[apName]
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        log.stampaInfo(f"TCP: chiusa connessione {apName or clientIp}, AP online: {len(connectedAps)}")


# --- WEBSOCKET CLIENT (Server esterno - stringhe CSV) ---
# Formati attesi dal server WebSocket:
#   "1,AA:BB:CC:DD:EE:FF,101"  -> associa MAC a UID, salva su disco e invia agli AP
#   "11,101"                    -> stop emergenza per UID

async def manageWsMessage(rawMessage: str):
    msg = str(rawMessage).strip()
    log.stampaInfo(f"WS RX: {msg[:120]}")

    if not msg:
        return

    if msg.startswith("{"):
        try:
            data = json.loads(msg)
            event = data.get("event")
            payload = data.get("payload", {})
        except json.JSONDecodeError:
            log.stampaWarning(f"WS RX: JSON non valido ({msg})")
            return

        if event == "DEVICE_CONNECTED":
            mac = str(payload.get("mac_address", "")).strip().upper()
            if len(mac) != 17:
                raise ValueError(f"MAC non valido: {mac[:30]}")

            uid = int(payload["device_id"])
            knownWatches[mac] = uid
            saveKnownWatches(knownWatches)
            log.stampaInfo(f"WS RX DEVICE_CONNECTED: {mac} -> uid={uid} (orologi noti: {len(knownWatches)})")

            out_login = OutDataLogin(pid=1, mac=mac, uid=uid)
            await sendToAp(out_login.toLine())
            return
        
        if event == "DEVICE_STOP_EMERGENCY":
            uid = int(payload["device_id"])
            log.stampaInfo(f"WS RX DEVICE_STOP_EMERGENCY: uid={uid}")
            await sendToAp(f"11,{uid}")
            return

        if event in ("NEW_DEVICE", "DEVICE_UPDATE", "NEW_EMERGENCY"):
            log.stampaInfo(f"WS RX {event}: payload={payload}")
            return

        log.stampaWarning(f"WS RX: evento JSON non gestito ({event})")
        return
    else:
        log.stampaWarning(f"WS RX: messaggio non JSON non gestito ({msg})")

    parts = [p.strip() for p in msg.split(",")]
    pid = int(parts[0])

    if pid == 11 and len(parts) == 2:
        uid = int(parts[1])
        log.stampaInfo(f"WS RX t11: stop emergenza uid={uid}")
        await sendToAp(f"11,{uid}")
    else:
        log.stampaWarning(f"WS RX: pacchetto non gestito o formato errato ({msg})")


async def wsClientLoop():
    while True:
        try:
            log.stampaInfo(f"WS: tentativo connessione a {WS_SERVER_URL}...")
            async with websockets.connect(WS_SERVER_URL) as websocket:
                state.wsConn = websocket
                log.stampaInfo(f"WS: connesso a {WS_SERVER_URL}")
                async for message in websocket:
                    try:
                        await manageWsMessage(message)
                    except (ValueError, IndexError, TypeError) as e:
                        log.stampaWarning(f"WS RX: messaggio non valido '{message}' ({e})")
        except (ConnectionClosed, OSError) as e:
            log.stampaWarning(f"WS: disconnesso ({e}), riconnessione tra 3s...")
        except Exception as e:
            log.stampaAllarme(f"WS: errore imprevisto ({e}), riconnessione tra 3s...")
        finally:
            state.wsConn = None

        await asyncio.sleep(3)