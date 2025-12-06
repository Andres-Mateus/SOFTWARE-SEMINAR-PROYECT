from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from database import Base


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    occupied = Column(Boolean, default=False)

    sessions = relationship("ParkingSession", back_populates="slot")


class ParkingSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(20), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False)
    check_in_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    check_out_at = Column(DateTime(timezone=True))
    amount = Column(Numeric(10, 2))

    slot = relationship("Slot", back_populates="sessions")
