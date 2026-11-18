from sqlalchemy.orm import Session #type: ignore

from assets.models.patient import Patient
from assets.schemas.patient import PatientCreate

def get_all_patients(db: Session) -> list[Patient] | None:
    return db.query(Patient).all()

def get_patient_by_id(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def create_patient(db: Session, patient_in: PatientCreate) -> Patient:
    db_patient = Patient(
        name=patient_in.name,
        surname=patient_in.surname,
    )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient_by_id(db: Session, patient_id: int) -> None:
    patient = get_patient_by_id(db, patient_id)

    if patient:
        db.delete(patient)
        db.commit()