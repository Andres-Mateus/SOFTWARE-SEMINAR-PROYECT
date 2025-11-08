# main.py
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlmodel import Session
from database import get_session, init_db
from models import UserP, Vehicle, Fee, Ticket, Payment, LotSpace
from schemas import (
    UserCreate,
    UserRead,
    VehicleCreate,
    VehicleRead,
    FeeCreate,
    FeeRead,
    TicketCreate,
    TicketRead,
    PaymentCreate,
    PaymentRead,
    LotSpaceCreate,
    LotSpaceRead,
)
import crud

app = FastAPI(title="Parking Core API")

api_router = APIRouter(prefix="/api/core", tags=["core"])


@app.on_event("startup")
def on_startup():
    init_db()


# === USERS ===
@api_router.post("/users", response_model=UserRead)
def crear_usuario(user: UserCreate, session: Session = Depends(get_session)):
    nuevo = UserP.from_orm(user)
    return crud.crear_registro(session, nuevo)


@api_router.get("/users", response_model=list[UserRead])
def listar_usuarios(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, UserP)


@api_router.get("/users/{id_user}", response_model=UserRead)
def obtener_usuario(id_user: str, session: Session = Depends(get_session)):
    registro = crud.obtener_por_id(session, UserP, id_user)
    if not registro:
        raise HTTPException(404, "Usuario no encontrado")
    return registro


@api_router.delete("/users/{id_user}")
def eliminar_usuario(id_user: str, session: Session = Depends(get_session)):
    registro = crud.eliminar_registro(session, UserP, id_user)
    if not registro:
        raise HTTPException(404, "Usuario no encontrado")
    return {"ok": True}


# === VEHICLES ===
@api_router.post("/vehicles", response_model=VehicleRead)
def crear_vehicle(data: VehicleCreate, session: Session = Depends(get_session)):
    nuevo = Vehicle.from_orm(data)
    return crud.crear_registro(session, nuevo)


@api_router.get("/vehicles", response_model=list[VehicleRead])
def listar_vehicles(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Vehicle)


# === FEE ===
@api_router.post("/fees", response_model=FeeRead)
def crear_fee(data: FeeCreate, session: Session = Depends(get_session)):
    nuevo = Fee.from_orm(data)
    return crud.crear_registro(session, nuevo)


@api_router.get("/fees", response_model=list[FeeRead])
def listar_fees(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Fee)


# === TICKETS ===
@api_router.post("/tickets", response_model=TicketRead)
def crear_ticket(data: TicketCreate, session: Session = Depends(get_session)):
    nuevo = Ticket.from_orm(data)
    return crud.crear_registro(session, nuevo)


@api_router.get("/tickets", response_model=list[TicketRead])
def listar_tickets(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Ticket)


# === PAYMENTS ===
@api_router.post("/payments", response_model=PaymentRead)
def crear_pago(data: PaymentCreate, session: Session = Depends(get_session)):
    nuevo = Payment.from_orm(data)
    return crud.crear_registro(session, nuevo)


@api_router.get("/payments", response_model=list[PaymentRead])
def listar_pagos(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Payment)


# === LOT SPACE ===
@api_router.post("/lotspaces", response_model=LotSpaceRead)
def crear_lotspace(data: LotSpaceCreate, session: Session = Depends(get_session)):
    nuevo = LotSpace.from_orm(data)
    return crud.crear_registro(session, nuevo)


@api_router.get("/lotspaces", response_model=list[LotSpaceRead])
def listar_lotspaces(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, LotSpace)


app.include_router(api_router)
