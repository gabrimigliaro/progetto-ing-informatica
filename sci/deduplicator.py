import asyncio

import log
from data import InDataLogin
from state import bufferPacchetti, inQueue

TEMPO_ATTESA = 2.0


def getChiave(packet):
    if isinstance(packet, InDataLogin):
        return (packet.pid, packet.mac)
    return (packet.pid, packet.uid)


def processPacket(packet):
    key = getChiave(packet)
    entry = bufferPacchetti.get(key)
    if entry is None:
        bufferPacchetti[key] = {
            "packet": packet,
            "count": 1,
            "timer": asyncio.create_task(windowExpired(key)),
        }
    else:
        entry["count"] += 1
        if packet.rssi > entry["packet"].rssi:
            entry["packet"] = packet


async def windowExpired(key):
    await asyncio.sleep(TEMPO_ATTESA)
    entry = bufferPacchetti.pop(key, None)
    if not entry:
        return
    packet = entry["packet"]
    if entry["count"] > 1:
        log.stampaInfo(
            f"DEDUP t{key[0]} {key[1]}: {entry['count']} copie, "
            f"scelto {packet.apName} (rssi {packet.rssi})"
        )
    await inQueue.put(packet)