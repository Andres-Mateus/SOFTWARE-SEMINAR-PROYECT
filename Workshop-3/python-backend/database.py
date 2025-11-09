"""Database utilities for the FastAPI core service."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select

from models import Fee, LotSpace, UserP, UserType, VehicleType

load_dotenv()


def _build_database_url() -> str:
    """Resolve the SQLAlchemy URL from environment variables with sensible defaults."""

    url = os.getenv("CORE_DATABASE_URL")
    if url:
        return url

    host = os.getenv("CORE_DB_HOST", "localhost")
    port = os.getenv("CORE_DB_PORT", "5432")
    user = os.getenv("CORE_DB_USER", "admon")
    password = os.getenv("CORE_DB_PASSWORD", "admon")
    database = os.getenv("CORE_DB_NAME", "parking")
    driver = os.getenv("CORE_DB_DRIVER", "postgresql")

    return f"{driver}://{user}:{password}@{host}:{port}/{database}"


DATABASE_URL = _build_database_url()
engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_DEBUG", "false").lower() == "true")


def seed_defaults(session: Session) -> None:
    """Ensure the database contains the base catalog required by the UI."""

    # System operator used for automated entries/exits triggered from the UI.
    if not session.get(UserP, "SYSTEM"):
        system_user = UserP(
            iduser="SYSTEM",
            username="System Operator",
            password="system",
            type=UserType.HUMAN,
        )
        session.add(system_user)

    # Default fee for car type so entries can be priced immediately.
    if (
        session.exec(select(Fee).where(Fee.type == VehicleType.CAR)).first() is None
    ):
        session.add(
            Fee(
                idfee="FEE-CAR-HOURLY",
                descfee="Standard car hourly rate",
                type=VehicleType.CAR,
                pricefee=4800.0,
            )
        )

    # Minimal set of slots consumed by the Web UI.
    default_slots = [
        ("A01", VehicleType.CAR),
        ("A02", VehicleType.CAR),
        ("A03", VehicleType.CAR),
        ("A04", VehicleType.CAR),
    ]
    for code, vehicle_type in default_slots:
        if session.get(LotSpace, code) is None:
            session.add(
                LotSpace(
                    idLotSpace=code,
                    type=vehicle_type,
                    totalSpace=1,
                    current_plate=None,
                )
            )

    session.commit()


def init_db() -> None:
    """Create tables and seed required data when the application boots."""

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_defaults(session)


@contextmanager
def session_context() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def get_session() -> Iterator[Session]:
    """Dependency used by FastAPI routes to access the database."""

    with Session(engine) as session:
        yield session
