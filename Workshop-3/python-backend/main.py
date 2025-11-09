"""FastAPI application exposing the parking core service."""

"""FastAPI entry point for the Workshop 3 core service."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import get_session, init_db
from models import Fee, LotSpace, Payment, Ticket, UserP, Vehicle, VehicleType
from schemas import (
    EntryRequest,
    EntryResponse,
    ExitRequest,
    ExitResponse,
    FeeCreate,
    FeeRead,
    LotSpaceCreate,
    LotSpaceRead,
    OverviewStats,
    PaymentCreate,
    PaymentRead,
    SessionItem,
    SessionsResponse,
    SlotItem,
    TicketCreate,
    TicketRead,
    UserCreate,
    UserRead,
    VehicleCreate,
    VehicleRead,
)
from services.lot_service import obtener_disponibilidad, resumen_ocupacion
from services.payment_service import registrar_salida_y_pago
from services.ticket_service import registrar_entrada
from services.vehicle_service import registrar_vehiculo

app = FastAPI(title="Parking Core API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


api = APIRouter(prefix="/api/core", tags=["Core"])


@api.get("/stats/overview", response_model=OverviewStats)
def get_overview_stats(session: Session = Depends(get_session)) -> OverviewStats:
    summary = resumen_ocupacion(session)
    total_slots = sum(data["total"] for data in summary.values())
    occupied = sum(data["occupied"] for data in summary.values())
    free = max(total_slots - occupied, 0)

    active_tickets = session.exec(select(Ticket).where(Ticket.exit.is_(None))).all()
    active_vehicles = len({ticket.licenseplate for ticket in active_tickets})

    car_fee = session.exec(select(Fee).where(Fee.type == VehicleType.CAR)).first()
    current_rate = round((car_fee.pricefee / 60) if car_fee else 0.0, 2)
    occupancy_percent = round((occupied / total_slots * 100) if total_slots else 0.0, 2)

    return OverviewStats(
        occupied=occupied,
        free=free,
        currentRatePerMinute=current_rate,
        activeVehicles=active_vehicles,
        occupancyPercent=occupancy_percent,
    )


@api.get("/sessions", response_model=SessionsResponse)
def get_recent_sessions(
    limit: int = Query(5, ge=1, le=50),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    session: Session = Depends(get_session),
) -> SessionsResponse:
    order_by = Ticket.entry.desc() if order == "desc" else Ticket.entry.asc()
    tickets = (
        session.exec(select(Ticket).order_by(order_by).limit(limit)).all()
    )

    items = [
        SessionItem(
            session_id=ticket.ticketid,
            plate=ticket.licenseplate,
            check_in_at=ticket.entry,
            check_out_at=ticket.exit,
        )
        for ticket in tickets
    ]
    return SessionsResponse(items=items)


@api.get("/slots", response_model=List[SlotItem])
def get_slots(session: Session = Depends(get_session)) -> List[SlotItem]:
    slots = obtener_disponibilidad(session)
    return [SlotItem(**slot) for slot in slots]


@api.post(
    "/entries",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_entry(
    request: EntryRequest, session: Session = Depends(get_session)
) -> EntryResponse:
    plate = request.plate.strip().upper()
    if not plate:
        raise HTTPException(status_code=400, detail="The plate field is required.")

    vehicle_type = request.vehicle_type or VehicleType.CAR
    vehicle = registrar_vehiculo(session, plate, vehicle_type)

    fee = (
        session.get(Fee, request.fee_id)
        if request.fee_id
        else session.exec(select(Fee).where(Fee.type == vehicle.type)).first()
    )
    if not fee:
        raise HTTPException(400, detail="No pricing rule configured for this vehicle type.")

    user_id = request.user_id or "SYSTEM"
    operator = session.get(UserP, user_id)
    if not operator:
        raise HTTPException(404, detail="Operator not registered in the system.")

    ticket = registrar_entrada(
        session=session,
        owner_document=request.owner_document or f"AUTO-{plate}",
        license_plate=plate,
        fee_id=fee.idfee,
        user_id=operator.iduser,
    )

    return EntryResponse(
        session_id=ticket.ticketid,
        plate=ticket.licenseplate,
        slot_code=ticket.slotcode or "",
        check_in_at=ticket.entry,
    )


@api.post("/exits", response_model=ExitResponse)
def register_exit(
    request: ExitRequest, session: Session = Depends(get_session)
) -> ExitResponse:
    plate = request.plate.strip().upper()
    ticket = session.exec(
        select(Ticket).where(Ticket.licenseplate == plate, Ticket.exit.is_(None))
    ).first()
    if not ticket:
        raise HTTPException(404, detail="Active ticket not found for this plate.")

    payment, minutes = registrar_salida_y_pago(session, ticket.ticketid)
    session.refresh(ticket)

    return ExitResponse(
        session_id=ticket.ticketid,
        plate=plate,
        minutes=minutes,
        amount=payment.payment,
        check_in_at=ticket.entry,
        check_out_at=ticket.exit,
    )


management_router = APIRouter(prefix="/api/core", tags=["Management"])


@management_router.post("/users", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    if session.get(UserP, user.iduser):
        raise HTTPException(status_code=400, detail="User already exists.")

    db_user = UserP.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserRead.model_validate(db_user)


@management_router.get("/users", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session)) -> List[UserRead]:
    users = session.exec(select(UserP)).all()
    return [UserRead.model_validate(user) for user in users]


@management_router.post("/vehicles", response_model=VehicleRead, status_code=201)
def create_vehicle(
    vehicle: VehicleCreate, session: Session = Depends(get_session)
) -> VehicleRead:
    vehicle.dateregistered = vehicle.dateregistered or datetime.utcnow()
    db_vehicle = Vehicle.from_orm(vehicle)
    session.add(db_vehicle)
    session.commit()
    session.refresh(db_vehicle)
    return VehicleRead.model_validate(db_vehicle)


@management_router.get("/vehicles", response_model=List[VehicleRead])
def list_vehicles(session: Session = Depends(get_session)) -> List[VehicleRead]:
    vehicles = session.exec(select(Vehicle)).all()
    return [VehicleRead.model_validate(vehicle) for vehicle in vehicles]


@management_router.post("/fees", response_model=FeeRead, status_code=201)
def create_fee(fee: FeeCreate, session: Session = Depends(get_session)) -> FeeRead:
    db_fee = Fee.from_orm(fee)
    session.add(db_fee)
    session.commit()
    session.refresh(db_fee)
    return FeeRead.model_validate(db_fee)


@management_router.get("/fees", response_model=List[FeeRead])
def list_fees(session: Session = Depends(get_session)) -> List[FeeRead]:
    fees = session.exec(select(Fee)).all()
    return [FeeRead.model_validate(fee) for fee in fees]


@management_router.post("/tickets", response_model=TicketRead, status_code=201)
def create_ticket(
    ticket: TicketCreate, session: Session = Depends(get_session)
) -> TicketRead:
    db_ticket = Ticket.from_orm(ticket)
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return TicketRead.model_validate(db_ticket)


@management_router.get("/tickets", response_model=List[TicketRead])
def list_tickets(session: Session = Depends(get_session)) -> List[TicketRead]:
    tickets = session.exec(select(Ticket)).all()
    return [TicketRead.model_validate(ticket) for ticket in tickets]


@management_router.post("/payments", response_model=PaymentRead, status_code=201)
def create_payment(
    payment: PaymentCreate, session: Session = Depends(get_session)
) -> PaymentRead:
    db_payment = Payment.from_orm(payment)
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)
    return PaymentRead.model_validate(db_payment)


@management_router.get("/payments", response_model=List[PaymentRead])
def list_payments(session: Session = Depends(get_session)) -> List[PaymentRead]:
    payments = session.exec(select(Payment)).all()
    return [PaymentRead.model_validate(payment) for payment in payments]


@management_router.post("/slots", response_model=LotSpaceRead, status_code=201)
def create_slot(slot: LotSpaceCreate, session: Session = Depends(get_session)) -> LotSpaceRead:
    db_slot = LotSpace.from_orm(slot)
    session.add(db_slot)
    session.commit()
    session.refresh(db_slot)
    return LotSpaceRead.model_validate(db_slot)


@management_router.get("/slots", response_model=List[LotSpaceRead])
def list_slots(session: Session = Depends(get_session)) -> List[LotSpaceRead]:
    slots = session.exec(select(LotSpace)).all()
    return [LotSpaceRead.model_validate(slot) for slot in slots]


app.include_router(api)
app.include_router(management_router)
