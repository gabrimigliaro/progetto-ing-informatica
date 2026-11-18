from sqlalchemy.orm import Session #type: ignore
from assets.models.device import Device #type: ignore
from assets.schemas.device import DeviceCreate
from typing import Optional

def create_device(db: Session, device: DeviceCreate) -> Device:
    db_device = Device(mac_address=device.mac_address)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_all_devices(db: Session) -> list[Device]:
    return db.query(Device).all()

def get_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    return db.query(Device).filter(Device.id == device_id).first()

def get_pending_devices(db: Session) -> Optional[Device]:
    return db.query(Device).filter(Device.status == "PENDING").all()

def get_connected_devices(db: Session) -> Optional[Device]:
    return db.query(Device).filter(Device.status == "CONNECTED").all()

def update_device_status(db: Session, device: Device, new_status: str = "CONNECTED") -> Device:
    device.status = new_status
    db.commit()
    db.refresh(device)
    return device

def delete_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    device = get_device_by_id(db, device_id)

    if device:
        db.delete(device)
        db.commit()