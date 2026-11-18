from datetime import datetime, timezone
from fastapi import HTTPException, status #type: ignore
from sqlalchemy.orm import Session, joinedload #type: ignore
from assets.models.emergency import Emergency
from assets.models.patient import Patient

def create_emergency(db: Session, p_id: int, emergency_type: int, bpm: int) -> Emergency:
    patient = db.query(Patient).filter(Patient.id == p_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paziente non trovato")

    db_emergency = Emergency(p_id=p_id, type=emergency_type, bpm=bpm)
    db.add(db_emergency)
    db.commit()
    db.refresh(db_emergency)
    return db_emergency

def get_emergencies(db: Session, only_unresolved: bool = False) -> list[Emergency]:
    query = (
        db.query(Emergency)
        .options(joinedload(Emergency.patient), joinedload(Emergency.resolver))
        .order_by(Emergency.created_at.desc())
    )
    
    if only_unresolved:
        query = query.filter(Emergency.resolved == False)
    return query.all()

def resolve_emergency(db: Session, emergency_id: int, user_id: int) -> Emergency:
    emergency = (
        db.query(Emergency)
        .options(joinedload(Emergency.patient), joinedload(Emergency.resolver))
        .filter(Emergency.id == emergency_id)
        .first()
    )
    if not emergency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergenza non trovata")
    
    if emergency.resolved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'emergenza risulta già risolta")

    emergency.resolved = True
    emergency.resolved_at = datetime.now(timezone.utc)
    emergency.resolved_by = user_id

    db.commit()
    db.refresh(emergency)
    return emergency

def delete_emergency(db: Session, emergency_id: int) -> None:
    emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    if not emergency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Emergenza non trovata")
    db.delete(emergency)
    db.commit()