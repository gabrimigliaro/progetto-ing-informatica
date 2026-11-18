from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Boolean, func #type: ignore
from sqlalchemy.orm import Mapped, mapped_column, relationship #type: ignore
from core.database import Base

class PatientDevice(Base):
    __tablename__ = "patient_device"

    id: Mapped[int] = mapped_column(primary_key=True)
    d_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="RESTRICT"))
    p_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")

    patient = relationship("Patient")
    device = relationship("Device")