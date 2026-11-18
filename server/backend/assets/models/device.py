from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func #type: ignore
from sqlalchemy.orm import Mapped, mapped_column #type: ignore
from sqlalchemy.dialects.postgresql import MACADDR #type: ignore
from core.database import Base #type: ignore

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    mac_address: Mapped[str | None] = mapped_column(MACADDR, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(Text, server_default="OPPO Watch")
    online: Mapped[bool] = mapped_column(Boolean, server_default="false")
    status: Mapped[str] = mapped_column(String(20), server_default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )