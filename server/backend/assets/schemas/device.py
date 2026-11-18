from datetime import datetime
from pydantic import BaseModel, ConfigDict #type: ignore

class DeviceCreate(BaseModel):
    mac_address: str

class DeviceResponse(BaseModel):
    id: int
    mac_address: str | None = None
    name: str
    online: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)