from datetime import datetime
from pydantic import BaseModel, ConfigDict #type: ignore

class PatientCreate(BaseModel):
    name: str
    surname: str

class PatientResponse(BaseModel):
    id: int
    name: str
    surname: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)