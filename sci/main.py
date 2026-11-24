import asyncio

import log
from router import outLoop, routeLoop, watchdogLoop
from server import ManTCPClient, wsClientLoop


async def main():
    asyncio.create_task(routeLoop())
    asyncio.create_task(outLoop())
    asyncio.create_task(wsClientLoop())
    asyncio.create_task(watchdogLoop())

    tcpServer = await asyncio.start_server(ManTCPClient, "0.0.0.0", 8000)
    log.stampaInfo("Server avviato: TCP 8000, Client WebSocket attivo.")

    await tcpServer.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

