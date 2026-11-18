from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict #type: ignore

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)