"""Database utilities for the FastAPI core service."""

from __future__ import annotations

import os
from typing import Dict

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()


def _build_database_url() -> str:
    """Return the database URL using environment variables.

    A DATABASE_URL variable takes precedence. Otherwise PostgreSQL
    connection parameters are read from DB_HOST, DB_USER, DB_PASSWORD and
    DB_NAME (with sensible defaults for local development).
    """

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "admon")
    password = os.getenv("DB_PASSWORD", "admon")
    database = os.getenv("DB_NAME", "parking")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _build_connect_args(database_url: str) -> Dict[str, object]:
    """Configure SQLAlchemy connect arguments depending on the backend."""

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


DATABASE_URL = _build_database_url()
CONNECT_ARGS = _build_connect_args(DATABASE_URL)
ECHO_SQL = os.getenv("SQL_ECHO", "false").lower() == "true"

engine = create_engine(DATABASE_URL, echo=ECHO_SQL, connect_args=CONNECT_ARGS)


def init_db() -> None:
    """Create database tables when the application starts."""

    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session for FastAPI dependencies."""

    with Session(engine) as session:
        yield session
