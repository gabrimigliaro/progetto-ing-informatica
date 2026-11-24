import asyncio
from storage import loadKnownWatches

lastSeen = {}

watchdogAlerted = set()

connectedAps = {}

knownWatches = loadKnownWatches()

bufferPacchetti = {}

inQueue = asyncio.Queue()

outQueue = asyncio.Queue()

wsConn = None