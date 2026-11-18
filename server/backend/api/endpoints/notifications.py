import json
import os
from fastapi import APIRouter, Depends #type: ignore
from pydantic import BaseModel #type: ignore
from sqlalchemy.orm import Session #type: ignore
from pywebpush import webpush, WebPushException #type: ignore
from core.database import get_db, SessionLocal
from assets.models.push_subscription import PushSubscription
from assets.schemas.notifications import SubscriptionKeys, PushSubscriptionSchema, UnsubscribeSchema
from api.deps import get_current_user

router = APIRouter()

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_CLAIMS = {"sub": "mailto:gabriele@gmigliaro.it"}

@router.post("/subscribe")
def subscribe_device(sub: PushSubscriptionSchema, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == sub.endpoint).first()
    if existing:
        existing.user_id = current_user.id
        existing.p256dh = sub.keys.p256dh
        existing.auth = sub.keys.auth
    else:
        new_sub = PushSubscription(
            user_id=current_user.id,
            endpoint=sub.endpoint,
            p256dh=sub.keys.p256dh,
            auth=sub.keys.auth,
        )
        db.add(new_sub)
    db.commit()
    return {"status": "subscribed"}

def send_push_to_all_subscribers(title: str, body: str, url: str = "/dashboard/emergencies"):
    db = SessionLocal()
    try:
        subscriptions = db.query(PushSubscription).all()
        payload = json.dumps({"title": title, "body": body, "url": url})

        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=payload,
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS,
                )
            except WebPushException as ex:
                if ex.response is not None and ex.response.status_code in (404, 410):
                    db.delete(sub)
        db.commit()
    finally:
        db.close()


@router.post("/unsubscribe")
def unsubscribe_device(sub: UnsubscribeSchema, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    deleted = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.endpoint == sub.endpoint,
            PushSubscription.user_id == current_user.id,
        )
        .delete()
    )
    db.commit()
    return {"status": "unsubscribed", "deleted": bool(deleted)}