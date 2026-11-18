from fastapi import APIRouter, Depends, HTTPException, status #type: ignore
from sqlalchemy.orm import Session #type: ignore
from assets.schemas.user import UserCreate, UserResponse
from assets.crud import user as user_crud
from assets.models.user import User
from api.deps import get_current_user #type: ignore
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    new_user = user_crud.create_user(db, user_in=user_in)
    return new_user


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_crud.delete_user(db=db, user=current_user)
    return None

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    user_crud.delete_user(db=db, user=user)
    return None