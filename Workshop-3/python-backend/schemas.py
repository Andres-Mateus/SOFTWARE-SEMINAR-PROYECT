"""Pydantic/SQLModel schemas exposed by the API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from models import UserType, VehicleType


# ----- USER -----
class UserCreate(SQLModel):
    iduser: str
    username: str
    password: str
    type: UserType

    class Config:
        use_enum_values = True


class UserRead(SQLModel):
    iduser: str
    username: str
    type: UserType

    class Config:
        use_enum_values = True


# ----- VEHICLE -----
class VehicleCreate(SQLModel):
    licenseplate: str
    type: VehicleType
    dateregistered: Optional[datetime] = None


class VehicleRead(VehicleCreate):
    pass


# ----- FEE -----
class FeeCreate(SQLModel):
    idfee: str
    descfee: str
    type: VehicleType
    pricefee: float


class FeeRead(FeeCreate):
    pass


# ----- TICKET -----
class TicketCreate(SQLModel):
    ownerdoc: str
    entry: Optional[datetime] = None
    exit: Optional[datetime] = None
    licenseplate: str
    idfee: str
    iduser: str
    slotcode: Optional[str] = None


class TicketRead(TicketCreate):
    ticketid: int


# ----- PAYMENT -----
class PaymentCreate(SQLModel):
    ticketid: int
    datepayment: Optional[datetime] = None
    payment: float


class PaymentRead(PaymentCreate):
    idpayment: int


# ----- LOT SPACE -----
class LotSpaceCreate(SQLModel):
    idLotSpace: str
    type: VehicleType
    totalSpace: int = 1
    current_plate: Optional[str] = None


class LotSpaceRead(LotSpaceCreate):
    pass


class OverviewStats(SQLModel):
    occupied: int
    free: int
    currentRatePerMinute: float
    activeVehicles: int
    occupancyPercent: float


class SessionItem(SQLModel):
    session_id: int
    plate: str
    check_in_at: datetime
    check_out_at: Optional[datetime] = None


class SessionsResponse(SQLModel):
    items: List[SessionItem]


class SlotItem(SQLModel):
    code: str
    type: VehicleType
    occupied: bool
    plate: Optional[str] = None


class EntryRequest(SQLModel):
    plate: str
    vehicle_type: Optional[VehicleType] = None
    owner_document: Optional[str] = None
    fee_id: Optional[str] = None
    user_id: Optional[str] = None


class EntryResponse(SQLModel):
    session_id: int
    plate: str
    slot_code: str
    check_in_at: datetime


class ExitRequest(SQLModel):
    plate: str


class ExitResponse(SQLModel):
    session_id: int
    plate: str
    minutes: int
    amount: float
    check_in_at: datetime
    check_out_at: datetime
