from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func #type: ignore
from sqlalchemy.orm import Mapped, mapped_column #type: ignore
from core.database import Base #type: ignore

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )