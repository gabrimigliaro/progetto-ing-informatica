from fastapi import APIRouter, Depends, HTTPException, status #type: ignore
from sqlalchemy.orm import Session #type: ignore
from assets.schemas.device import DeviceResponse, DeviceCreate
from assets.crud import device as device_crud
from assets.models.user import User
from api.deps import get_current_user #type: ignore
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_new_device(device: DeviceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return device_crud.create_device(db=db, device=device)

@router.get("/", response_model=list[DeviceResponse])
def read_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return device_crud.get_all_devices(db=db)

@router.get("/pendings", response_model=list[DeviceResponse])
def read_pending_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return device_crud.get_pending_devices(db=db)

@router.get("/connected", response_model=list[DeviceResponse])
def read_connected_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return device_crud.get_connected_devices(db=db)


@router.patch("/{device_id}/connect", response_model=DeviceResponse)
def connect_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    device = device_crud.get_device_by_id(db=db, device_id=device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo non trovato")
    
    updated_device = device_crud.update_device_status(db=db, device=device, new_status="CONNECTED")
    return updated_device

@router.patch("/{device_id}/refuse", response_model=DeviceResponse)
def refuse_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    device = device_crud.get_device_by_id(db=db, device_id=device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo non trovato")
    
    updated_device = device_crud.update_device_status(db=db, device=device, new_status="REFUSED")
    return updated_device

@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return device_crud.delete_device_by_id(db, device_id)