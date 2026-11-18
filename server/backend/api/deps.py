import jwt #type: ignore
from fastapi import Request, Depends, HTTPException, status  #type: ignore
from fastapi.security import OAuth2PasswordBearer  #type: ignore
from sqlalchemy.orm import Session #type: ignore
from core.database import get_db
from core.security import SECRET_KEY, ALGORITHM
from assets.crud.user import get_user_by_id
from assets.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")


    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide o sessione scaduta",
        headers={"WWW-Authenticate": "Bearer"},
    )


    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception

    user = get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
        
    return user