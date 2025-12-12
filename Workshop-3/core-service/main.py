# main.py
import math

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_session
from schemas import (
    EntryRequest,
    EntryResponse,
    ExitRequest,
    ExitResponse,
    SessionOut,
    SlotOut,
    StatsOut,
)
from services.parking_service import (
    ensure_slots,
    format_plate_display,
    get_overview,
    list_sessions,
    list_slots,
    register_entry,
    register_exit,
    PLATE_REGEX,
    RATE_PER_MINUTE,
)

CURRENCY = "COP"

app = FastAPI(title="Parking Core Service", openapi_url="/api/core/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        ensure_slots(session)


def get_db():
    with get_session() as session:
        yield session


@app.get("/api/core/stats/overview", response_model=StatsOut)
def stats_overview(db: Session = Depends(get_db)):
    return get_overview(db)


@app.get("/api/core/sessions", response_model=list[SessionOut])
def recent_sessions(
    limit: int = Query(5, ge=1, le=50),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    sessions = list_sessions(db, limit=limit, order=order)
    return [
        SessionOut(
            plate=format_plate_display(s.plate),
            slot_code=s.slot.code,
            slot=s.slot.code,
            check_in_at=s.check_in_at,
            check_in=s.check_in_at,
            check_out_at=s.check_out_at,
            check_out=s.check_out_at,
            amount=float(s.amount) if s.amount is not None else None,
        )
        for s in sessions
    ]


@app.get("/api/core/slots", response_model=list[SlotOut])
def slots(db: Session = Depends(get_db)):
    return list_slots(db)


@app.post("/api/core/entries", response_model=EntryResponse)
def entries(payload: EntryRequest, db: Session = Depends(get_db)):
    plate = (payload.plate or "").strip().upper()
    if not plate or not PLATE_REGEX.fullmatch(plate):
        raise HTTPException(status_code=400, detail="Invalid plate format. Use ABC-123.")

    try:
        session = register_entry(db, plate)
    except ValueError as exc:
        if str(exc) == "NO_SLOTS":
            raise HTTPException(status_code=409, detail="No slots available")
        raise HTTPException(status_code=400, detail=str(exc))

    return EntryResponse(
        plate=format_plate_display(session.plate),
        slot_code=session.slot.code,
        slot=session.slot.code,
        check_in_at=session.check_in_at,
        check_in=session.check_in_at,
    )


@app.post("/api/core/exits", response_model=ExitResponse)
def exits(payload: ExitRequest, db: Session = Depends(get_db)):
    plate = (payload.plate or "").strip().upper()
    if not plate or not PLATE_REGEX.fullmatch(plate):
        raise HTTPException(status_code=400, detail="Invalid plate format. Use ABC-123.")

    try:
        session = register_exit(db, plate)
    except ValueError as exc:
        if str(exc) == "ACTIVE_SESSION_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Active session not found")
        raise HTTPException(status_code=400, detail=str(exc))

    check_in = session.check_in_at
    check_out = session.check_out_at

    minutes = 1
    if check_in and check_out:
        total_seconds = (check_out - check_in).total_seconds()
        minutes = max(1, math.ceil(total_seconds / 60))

    amount = float(session.amount or 0)
    rate_per_minute = float(RATE_PER_MINUTE)
    rate_per_hour = float(RATE_PER_MINUTE * 60)

    display_plate = format_plate_display(session.plate)

    return ExitResponse(
        plate=display_plate,
        slot_code=session.slot.code,
        slot=session.slot.code,
        check_in_at=check_in,
        check_in=check_in,
        minutes=minutes,
        amount=amount,
        rate_per_minute=rate_per_minute,
        rate_per_hour=rate_per_hour,
        currency=CURRENCY,
        check_out_at=check_out,
        check_out=check_out,
    )


@app.get("/")
def root():
    return {"message": "Core service is running"}