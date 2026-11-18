from sqlalchemy.exc import IntegrityError #type: ignore

from core.database import SessionLocal

from assets.schemas.device import DeviceCreate

from assets.crud import emergency as emergency_crud
from assets.crud import device as device_crud
from assets.crud import patient_device as patient_device_crud

def save_emergency_to_db(p_id: int, emergency_type: int, bpm: int) -> dict:
    db = SessionLocal()
    try:
        new_em = emergency_crud.create_emergency(db=db, p_id=p_id, emergency_type=emergency_type, bpm=bpm)
        return {
            "id": new_em.id,
            "p_id": new_em.p_id,
            "bpm": new_em.bpm,
            "type": new_em.type,
            "resolved": new_em.resolved,
            "created_at": new_em.created_at.isoformat(),
            "resolved_at": None,
            "resolved_by": None,
            "patient": {
                "id": new_em.patient.id,
                "name": new_em.patient.name,
                "surname": new_em.patient.surname,
            } if new_em.patient else None,
        }
    finally: db.close()

def save_device_to_db(mac_address: str) -> dict:
    db = SessionLocal()
    try:
        device_in = DeviceCreate(mac_address=mac_address)
        new_em = device_crud.create_device(db=db, device=device_in)
        return {
            "id": new_em.id,
            "mac_address": new_em.mac_address,
            "name": new_em.name,
            "online": new_em.online,
            "status": new_em.status,
            "created_at": new_em.created_at.isoformat(),
        }
    except IntegrityError:
        db.rollback()
        print(f"Dispositivo con MAC {mac_address} già presente nel DB.", flush=True)

        return {
            "status": "error",
            "message": "Mac Address already in db."
        }
    finally: db.close()

def get_patient_by_device_id(device_id: int) -> dict | None:
    db = SessionLocal()
    try:
        association = patient_device_crud.get_association_from_device_id(db=db, device_id=device_id)
        
        if not association or not association.patient:
            return None

        return {
            "id": association.patient.id,
            "name": association.patient.name,
            "surname": association.patient.surname,
        }
    finally:
        db.close()