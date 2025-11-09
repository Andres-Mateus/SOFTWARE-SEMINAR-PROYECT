"""SQLModel ORM definitions used by the FastAPI core service."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# -----------------------------
#           ENUM TYPES
# -----------------------------


class UserType(str, Enum):
    MACHINE = "MACHINE REGISTER"
    HUMAN = "HUMAN REGISTER"


class VehicleType(str, Enum):
    CAR = "CAR"
    MOTORCYCLE = "MOTORCYCLE"
    TRUCK = "TRUCK"
    BUS = "BUS"
    VAN = "VAN"
    SUV = "SUV"
    BICYCLE = "BICYCLE"
    ELECTRIC_BICYCLE = "ELECTRIC BICYCLE"
    ELECTRIC_SCOOTER = "ELECTRIC SCOOTER"


# -----------------------------
#           TABLES
# -----------------------------


class UserP(SQLModel, table=True):
    __tablename__ = "userp"

    iduser: str = Field(primary_key=True, max_length=15)
    username: str = Field(max_length=30)
    password: str = Field(max_length=35)
    type: UserType

    tickets: List["Ticket"] = Relationship(back_populates="user")


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicle"

    licenseplate: str = Field(primary_key=True, max_length=10)
    type: VehicleType
    dateregistered: datetime = Field(default_factory=datetime.utcnow)

    tickets: List["Ticket"] = Relationship(back_populates="vehicle")


class Fee(SQLModel, table=True):
    __tablename__ = "fee"

    idfee: str = Field(primary_key=True, max_length=10)
    descfee: str = Field(max_length=255)
    type: VehicleType
    pricefee: float

    tickets: List["Ticket"] = Relationship(back_populates="fee")


class Ticket(SQLModel, table=True):
    __tablename__ = "ticket"

    ticketid: Optional[int] = Field(default=None, primary_key=True)
    ownerdoc: str = Field(max_length=40)
    entry: datetime = Field(default_factory=datetime.utcnow)
    exit: Optional[datetime] = None

    licenseplate: str = Field(foreign_key="vehicle.licenseplate")
    idfee: str = Field(foreign_key="fee.idfee")
    iduser: str = Field(foreign_key="userp.iduser")
    slotcode: Optional[str] = Field(default=None, foreign_key="lotspace.idLotSpace")

    vehicle: Optional[Vehicle] = Relationship(back_populates="tickets")
    fee: Optional[Fee] = Relationship(back_populates="tickets")
    user: Optional[UserP] = Relationship(back_populates="tickets")
    slot: Optional["LotSpace"] = Relationship(back_populates="tickets")
    payments: List["Payment"] = Relationship(back_populates="ticket")


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    idpayment: Optional[int] = Field(default=None, primary_key=True)
    ticketid: int = Field(foreign_key="ticket.ticketid")
    datepayment: datetime = Field(default_factory=datetime.utcnow)
    payment: float

    ticket: Optional[Ticket] = Relationship(back_populates="payments")


class LotSpace(SQLModel, table=True):
    __tablename__ = "lotspace"

    idLotSpace: str = Field(primary_key=True, max_length=10)
    type: VehicleType
    totalSpace: int = 1
    current_plate: Optional[str] = Field(default=None, max_length=10)

    tickets: List["Ticket"] = Relationship(back_populates="slot")
