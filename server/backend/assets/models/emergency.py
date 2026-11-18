from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, func #type: ignore
from sqlalchemy.orm import Mapped, mapped_column, relationship #type: ignore
from core.database import Base

class Emergency(Base):
    __tablename__ = "emergencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    p_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    bpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    patient = relationship("Patient")
    resolver = relationship("User")