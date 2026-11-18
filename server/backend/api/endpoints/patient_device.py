from fastapi import APIRouter, Depends, status #type: ignore
from sqlalchemy.orm import Session #type: ignore
from assets.schemas.patient_device import AssociationCreate, AssociationResponse
from assets.models.user import User
from assets.crud import patient_device as assoc_crud
from api.deps import get_current_user
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=AssociationResponse, status_code=status.HTTP_201_CREATED)
def create_association(data: AssociationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return assoc_crud.assign_device_to_patient(db=db, patient_id=data.p_id, device_id=data.d_id)

@router.get("/", response_model=list[AssociationResponse])
def read_active_associations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return assoc_crud.get_active_associations(db=db)

@router.patch("/{association_id}/unassign", response_model=AssociationResponse)
def close_association(association_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return assoc_crud.unassign_device(db=db, association_id=association_id)