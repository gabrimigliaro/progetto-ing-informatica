import os
from typing import Generator
from sqlalchemy import create_engine #type: ignore
from sqlalchemy.orm import DeclarativeBase, sessionmaker #type: ignore

DATABASE_URL = os.getenv("DATABASE_URL", None)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()