from pydantic import BaseModel, EmailStr #type: ignore

class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscriptionSchema(BaseModel):
    endpoint: str
    keys: SubscriptionKeys

class UnsubscribeSchema(BaseModel):
    endpoint: str