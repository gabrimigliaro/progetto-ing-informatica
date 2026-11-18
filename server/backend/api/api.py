from fastapi import APIRouter #type: ignore
from api.endpoints import users, auth, devices, patients, patient_device, emergencies, ws, notifications

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])
api_router.include_router(patient_device.router, prefix="/associations", tags=["Associations"])
api_router.include_router(emergencies.router, prefix="/emergencies", tags=["Emergencies"])
api_router.include_router(ws.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(notifications.router, prefix="/push", tags=["Push Notifications"])