from fastapi import HTTPException, status #type: ignore
from sqlalchemy.orm import Session, joinedload #type: ignore
from assets.models.patient_device import PatientDevice
from assets.models.patient import Patient
from assets.models.device import Device

def assign_device_to_patient(db: Session, patient_id: int, device_id: int) -> PatientDevice:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paziente non trovato")

    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo non trovato")
    
    if device.status != "CONNECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Il dispositivo deve essere prima connesso (CONNECTED) per essere associato"
        )

    active_patient = db.query(PatientDevice).filter(
        PatientDevice.p_id == patient_id,
        PatientDevice.is_active == True
    ).first()
    if active_patient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Questo paziente ha già un dispositivo attivo associato."
        )

    active_device = db.query(PatientDevice).filter(
        PatientDevice.d_id == device_id,
        PatientDevice.is_active == True
    ).first()
    if active_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Questo dispositivo è già associato a un altro paziente."
        )

    db_assoc = PatientDevice(p_id=patient_id, d_id=device_id)
    db.add(db_assoc)
    db.commit()
    db.refresh(db_assoc)
    return db_assoc

def get_active_associations(db: Session) -> list[PatientDevice]:
    return (
        db.query(PatientDevice)
        .options(joinedload(PatientDevice.patient), joinedload(PatientDevice.device))
        .filter(PatientDevice.is_active == True)
        .all()
    )

def unassign_device(db: Session, association_id: int) -> PatientDevice:
    assoc = db.query(PatientDevice).filter(
        PatientDevice.id == association_id,
        PatientDevice.is_active == True
    ).first()
    
    if not assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associazione attiva non trovata")

    assoc.is_active = False
    db.commit()
    db.refresh(assoc)
    return assoc

def get_association_from_device_id(db: Session, device_id: int) -> PatientDevice | None:
    return (
        db.query(PatientDevice)
        .options(joinedload(PatientDevice.patient), joinedload(PatientDevice.device))
        .filter(
            PatientDevice.d_id == device_id,
            PatientDevice.is_active == True
        )
        .first()
    )