import os
import pyotp #type: ignore
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Header, Cookie, status #type: ignore
from assets.utils.ws import parsePacket
from core.database import SessionLocal
from api.deps import get_current_user

router = APIRouter()

WS_TOTP_SECRET = os.getenv("WEBSOCKET_SECRET", None)
totp = pyotp.TOTP(WS_TOTP_SECRET)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_to_dashboards(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


def is_authorized(websocket: WebSocket, device_token: str | None) -> bool:
    # 1. Controlla se arriva un codice TOTP valido dal dispositivo (header o query)
    if device_token:
        clean_token = device_token.removeprefix("Bearer ").strip()
        if clean_token.isdigit():
            return totp.verify(clean_token, valid_window=1)

    # 2. Altrimenti controlla il cookie JWT della dashboard React tramite get_current_user
    db = SessionLocal()
    try:
        user = get_current_user(request=websocket, db=db)
        return user is not None
    except Exception:
        return False
    finally:
        db.close()


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, token: str | None = Query(default=None), x_device_token: str | None = Header(default=None)):
    device_token = x_device_token or token

    if not is_authorized(websocket, device_token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        while True:
            rawData: str = await websocket.receive_text()
            print(f"Arrivato pacchetto: {rawData}", flush=True)

            await parsePacket(rawData, manager)

    except WebSocketDisconnect:
        manager.disconnect(websocket)