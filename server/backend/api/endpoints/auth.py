from fastapi import APIRouter, Depends, HTTPException, Response #type: ignore
from sqlalchemy.orm import Session #type: ignore
from assets.schemas.auth import UserLogin
from assets.crud import user as user_crud
from core.database import get_db
from core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(login_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenziali non valide")

    access_token = create_access_token(data={"sub": str(user.id)})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800
    )
    return {"message": "Login effettuato"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    return {"message": "Logout effettuato"}