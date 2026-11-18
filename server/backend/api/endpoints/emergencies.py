from fastapi import APIRouter, Depends, Query, status #type: ignore
from sqlalchemy.orm import Session #type: ignore
from assets.schemas.emergency import EmergencyCreate, EmergencyResponse
from assets.models.user import User
from assets.crud import emergency as emergency_crud
from api.deps import get_current_user
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=EmergencyResponse, status_code=status.HTTP_201_CREATED)
def trigger_emergency(data: EmergencyCreate, db: Session = Depends(get_db)):
    return emergency_crud.create_emergency(db=db, p_id=data.p_id, emergency_type=data.type)

@router.get("/", response_model=list[EmergencyResponse])
def read_emergencies(unresolved_only: bool = Query(False, description="Filtra solo le emergenze attive non risolte"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return emergency_crud.get_emergencies(db=db, only_unresolved=unresolved_only)

@router.patch("/{emergency_id}/resolve", response_model=EmergencyResponse)
def resolve_emergency(emergency_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return emergency_crud.resolve_emergency(db=db, emergency_id=emergency_id, user_id=current_user.id)

@router.delete("/{emergency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emergency(emergency_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emergency_crud.delete_emergency(db=db, emergency_id=emergency_id)
    return None