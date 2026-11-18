from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict #type: ignore
from assets.schemas.patient import PatientResponse
from assets.schemas.user import UserResponse

class EmergencyCreate(BaseModel):
    p_id: int
    type: int
    bpm: int

class EmergencyResponse(BaseModel):
    id: int
    p_id: int
    bpm: Optional[int] = None
    type: int
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None

    patient: Optional[PatientResponse] = None
    resolver: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)