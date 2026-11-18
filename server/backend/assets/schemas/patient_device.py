from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict #type: ignore
from assets.schemas.patient import PatientResponse
from assets.schemas.device import DeviceResponse

class AssociationCreate(BaseModel):
    p_id: int
    d_id: int

class AssociationResponse(BaseModel):
    id: int
    d_id: int
    p_id: int
    assigned_at: datetime
    is_active: bool
    
    patient: Optional[PatientResponse] = None
    device: Optional[DeviceResponse] = None

    model_config = ConfigDict(from_attributes=True)