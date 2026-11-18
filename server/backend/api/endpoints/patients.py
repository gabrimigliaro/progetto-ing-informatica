from fastapi import APIRouter, Depends, HTTPException, status #type: ignore
from sqlalchemy.orm import Session #type: ignore
from assets.schemas.patient import PatientResponse, PatientCreate
from assets.crud import patient as patient_crud
from assets.models.user import User
from api.deps import get_current_user #type: ignore
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_new_patient(patient_in: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return patient_crud.create_patient(db, patient_in=patient_in)

@router.get("/", response_model=list[PatientResponse])
def read_all_patients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return patient_crud.get_all_patients(db)

@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return patient_crud.get_patient_by_id(db, patient_id)

@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return patient_crud.delete_patient_by_id(db, patient_id)