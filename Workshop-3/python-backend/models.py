"""
The script funtion is create and enable the models for each table of DB
"""

from enum import Enum
from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

# -----------------------------
#           ENUM TYPES
# -----------------------------


class UserType(str, Enum):
    MACHINE_REGISTER = "MACHINE REGISTER"
    HUMAN_REGISTER = "HUMAN REGISTER"


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

    idUser: str = Field(primary_key=True, max_length=15)
    username: str = Field(max_length=30)
    password: str = Field(max_length=35)
    type: UserType

    tickets: List["Ticket"] = Relationship(back_populates="user")


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicle"

    licenseplate: str = Field(primary_key=True, max_length=10)
    type: VehicleType
    dateregistered: date

    tickets: List["Ticket"] = Relationship(back_populates="vehicle")


class Fee(SQLModel, table=True):
    __tablename__ = "fee"

    idFee: str = Field(primary_key=True, max_length=10)
    descFee: str = Field(max_length=255)
    type: VehicleType
    priceFee: float

    tickets: List["Ticket"] = Relationship(back_populates="fee")


class Ticket(SQLModel, table=True):
    __tablename__ = "ticket"

    ticketid: Optional[int] = Field(default=None, primary_key=True)
    ownerdoc: str = Field(max_length=15)
    entry: date
    exit: Optional[date] = None

    licenseplate: str = Field(foreign_key="vehicle.licenseplate")
    idFee: str = Field(foreign_key="fee.idFee")
    idUser: str = Field(foreign_key="userp.idUser")

    # Relaciones
    vehicle: Optional[Vehicle] = Relationship(back_populates="tickets")
    fee: Optional[Fee] = Relationship(back_populates="tickets")
    user: Optional[UserP] = Relationship(back_populates="tickets")
    payments: List["Payment"] = Relationship(back_populates="ticket")


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    idpayment: Optional[int] = Field(default=None, primary_key=True)
    ticketid: int = Field(foreign_key="ticket.ticketid")
    datepayment: date
    payment: float

    ticket: Optional[Ticket] = Relationship(back_populates="payments")


class LotSpace(SQLModel, table=True):
    __tablename__ = "lotspace"

    idLotSpace: str = Field(primary_key=True, max_length=10)
    type: VehicleType
    totalSpace: int
