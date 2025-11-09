"""
Main Script of Core-Service
"""

from fastapi import FastAPI, Depends, HTTPException
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
from services.ticket_service import registrar_entrada
from services.payment_service import registrar_salida_y_pago
from services.lot_service import obtener_disponibilidad
from services.vehicle_service import registrar_vehiculo

app = FastAPI(title="Parqueadero API")


@app.on_event("startup")
def on_startup():
    init_db()


# === USERS ===
@app.post("/users/", response_model=UserRead)
def crear_usuario(user: UserCreate, session: Session = Depends(get_session)):
    nuevo = UserP.from_orm(user)
    return crud.crear_registro(session, nuevo)


@app.get("/users/", response_model=list[UserRead])
def listar_usuarios(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, UserP)


@app.get("/users/{idUser}", response_model=UserRead)
def obtener_usuario(idUser: str, session: Session = Depends(get_session)):
    registro = crud.obtener_por_id(session, UserP, idUser)
    if not registro:
        raise HTTPException(404, "Usuario no encontrado")
    return registro


@app.delete("/users/{idUser}")
def eliminar_usuario(idUser: str, session: Session = Depends(get_session)):
    registro = crud.eliminar_registro(session, UserP, idUser)
    if not registro:
        raise HTTPException(404, "Usuario no encontrado")
    return {"ok": True}


# === VEHICLES ===
@app.post("/vehicles/", response_model=VehicleRead)
def crear_vehicle(data: VehicleCreate, session: Session = Depends(get_session)):
    nuevo = Vehicle.from_orm(data)
    return crud.crear_registro(session, nuevo)


@app.get("/vehicles/", response_model=list[VehicleRead])
def listar_vehicles(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Vehicle)


# === FEE ===
@app.post("/fees/", response_model=FeeRead)
def crear_fee(data: FeeCreate, session: Session = Depends(get_session)):
    nuevo = Fee.from_orm(data)
    return crud.crear_registro(session, nuevo)


@app.get("/fees/", response_model=list[FeeRead])
def listar_fees(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Fee)


# === TICKETS ===
@app.post("/tickets/", response_model=TicketRead)
def crear_ticket(data: TicketCreate, session: Session = Depends(get_session)):
    nuevo = Ticket.from_orm(data)
    return crud.crear_registro(session, nuevo)


@app.get("/tickets/", response_model=list[TicketRead])
def listar_tickets(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Ticket)


# === PAYMENTS ===
@app.post("/payments/", response_model=PaymentRead)
def crear_pago(data: PaymentCreate, session: Session = Depends(get_session)):
    nuevo = Payment.from_orm(data)
    return crud.crear_registro(session, nuevo)


@app.get("/payments/", response_model=list[PaymentRead])
def listar_pagos(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, Payment)


# === LOT SPACE ===
@app.post("/lotspaces/", response_model=LotSpaceRead)
def crear_lotspace(data: LotSpaceCreate, session: Session = Depends(get_session)):
    nuevo = LotSpace.from_orm(data)
    return crud.crear_registro(session, nuevo)


@app.get("/lotspaces/", response_model=list[LotSpaceRead])
def listar_lotspaces(session: Session = Depends(get_session)):
    return crud.obtener_todos(session, LotSpace)


@app.post("/entrada/")
def entrada(
    ownerdoc: str,
    licenseplate: str,
    idFee: str,
    idUser: str,
    session: Session = Depends(get_session),
):
    return registrar_entrada(session, ownerdoc, licenseplate, idFee, idUser)


@app.post("/salida/{ticketid}")
def salida(ticketid: int, session: Session = Depends(get_session)):
    return registrar_salida_y_pago(session, ticketid)


@app.get("/disponibilidad/")
def disponibilidad(session: Session = Depends(get_session)):
    return obtener_disponibilidad(session)


@app.post("/vehiculos/")
def nuevo_vehiculo(
    licenseplate: str, type: str, session: Session = Depends(get_session)
):
    return registrar_vehiculo(session, licenseplate, type)
