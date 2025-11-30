from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_session
from models import ParkingSession, Slot

RATE_PER_MINUTE = 0.05
DEFAULT_SLOTS = ["A01", "A02", "A03", "B01", "B02"]


def ensure_slots(session: Session):
    existing_codes = {code for (code,) in session.execute(select(Slot.code)).all()}
    for code in DEFAULT_SLOTS:
        if code not in existing_codes:
            session.add(Slot(code=code, occupied=False))


def get_overview(session: Session):
    total_slots = session.scalar(select(func.count(Slot.id))) or 0
    occupied = session.scalar(select(func.count(Slot.id)).where(Slot.occupied.is_(True))) or 0
    free = total_slots - occupied

    active_vehicles = session.scalar(select(func.count(ParkingSession.id)).where(ParkingSession.check_out_at.is_(None))) or 0
    occupancy_percent = (occupied / total_slots * 100) if total_slots else 0

    return {
        "occupied": occupied,
        "free": max(free, 0),
        "activeVehicles": active_vehicles,
        "occupancyPercent": round(occupancy_percent, 2),
        "currentRatePerMinute": RATE_PER_MINUTE,
    }


def list_sessions(session: Session, limit: int = 5, order: str = "desc") -> List[ParkingSession]:
    ordering = ParkingSession.check_in_at.desc() if order == "desc" else ParkingSession.check_in_at.asc()
    return session.scalars(select(ParkingSession).order_by(ordering).limit(limit)).all()


def list_slots(session: Session):
    active_sessions = {s.slot_id: s for s in session.scalars(
        select(ParkingSession).where(ParkingSession.check_out_at.is_(None))
    ).all()}
    slots = session.scalars(select(Slot)).all()
    result = []
    for slot in slots:
        active = active_sessions.get(slot.id)
        result.append({
            "code": slot.code,
            "occupied": slot.occupied,
            "plate": active.plate if active else None
        })
    return result


def register_entry(session: Session, plate: str) -> ParkingSession:
    existing = session.scalars(
        select(ParkingSession).where(ParkingSession.plate == plate, ParkingSession.check_out_at.is_(None))
    ).first()
    if existing:
        return existing

    free_slot = session.scalars(select(Slot).where(Slot.occupied.is_(False)).order_by(Slot.code)).first()
    if not free_slot:
        raise ValueError("No slots available")

    free_slot.occupied = True
    new_session = ParkingSession(
        plate=plate,
        slot=free_slot,
        check_in_at=datetime.now(timezone.utc)
    )
    session.add(new_session)
    return new_session


def register_exit(session: Session, plate: str) -> ParkingSession:
    parking_session = session.scalars(
        select(ParkingSession).where(ParkingSession.plate == plate, ParkingSession.check_out_at.is_(None))
    ).first()
    if not parking_session:
        raise ValueError("Active session not found")

    now = datetime.now(timezone.utc)
    parking_session.check_out_at = now

    minutes = max(1, int((now - parking_session.check_in_at).total_seconds() // 60))
    parking_session.amount = round(minutes * RATE_PER_MINUTE, 2)

    slot = parking_session.slot
    if slot:
        slot.occupied = False

    return parking_session


def init_database():
    with get_session() as session:
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        ensure_slots(session)
