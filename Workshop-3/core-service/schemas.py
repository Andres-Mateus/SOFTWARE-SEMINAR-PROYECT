"""
The script funtion is create the schemas model for futute actions for the API
"""

from typing import Optional
from datetime import date
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
    dateregistered: date


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
    entry: date
    exit: Optional[date] = None
    licenseplate: str
    idfee: str
    iduser: str


class TicketRead(TicketCreate):
    ticketid: int


# ----- PAYMENT -----
class PaymentCreate(SQLModel):
    ticketid: int
    datepayment: date
    payment: float


class PaymentRead(PaymentCreate):
    idpayment: int


# ----- LOT SPACE -----
class LotSpaceCreate(SQLModel):
    idLotSpace: str
    type: VehicleType
    totalSpace: int


class LotSpaceRead(LotSpaceCreate):
    pass
