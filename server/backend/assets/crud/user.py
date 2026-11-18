from sqlalchemy.orm import Session #type: ignore

from assets.models.user import User
from assets.schemas.user import UserCreate

from core.security import hash_password

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_pwd = hash_password(user_in.password)
    
    db_user = User(
        name=user_in.name,
        surname=user_in.surname,
        email=user_in.email,
        password=hashed_pwd
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()