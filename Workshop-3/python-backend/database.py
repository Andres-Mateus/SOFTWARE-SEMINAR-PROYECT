"""Database utilities for the FastAPI core service."""

from __future__ import annotations

import os
from typing import Dict
from urllib.parse import quote, urlparse, urlunparse

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()


def _encode_component(value: str | None) -> str | None:
    """Return a percent-encoded representation or ``None``."""

    if value is None:
        return None
    # ``quote`` defaults to UTF-8, covering credentials with accents or spaces.
    return quote(value, safe="")


def _sanitize_database_url(database_url: str) -> str:
    """Percent-encode credentials and database names when needed."""

    try:
        parsed = urlparse(database_url)
    except ValueError:
        return database_url

    if not parsed.scheme.startswith("postgresql"):
        return database_url

    username = _encode_component(parsed.username)
    password = _encode_component(parsed.password)
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""

    userinfo = ""
    if username is not None:
        if password is not None:
            userinfo = f"{username}:{password}@"
        else:
            userinfo = f"{username}@"
    elif password is not None:
        userinfo = f":{password}@"

    if hostname and ":" in hostname and not hostname.startswith("["):
        host_segment = f"[{hostname}]{port}"
    else:
        host_segment = f"{hostname}{port}"

    path = parsed.path or ""
    if path and path != "/":
        path = "/" + quote(path.lstrip("/"), safe="")

    return urlunparse(
        (
            parsed.scheme,
            f"{userinfo}{host_segment}",
            path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def _build_database_url() -> str:
    """Return the database URL using environment variables.

    A DATABASE_URL variable takes precedence. Otherwise PostgreSQL
    connection parameters are read from DB_HOST, DB_USER, DB_PASSWORD and
    DB_NAME (with sensible defaults for local development).
    """

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return _sanitize_database_url(database_url)

    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "admon")
    password = os.getenv("DB_PASSWORD", "admon")
    database = os.getenv("DB_NAME", "parking")
    port = os.getenv("DB_PORT", "5432")
    safe_user = _encode_component(user) or ""
    safe_password = _encode_component(password) or ""
    safe_database = _encode_component(database) or ""
    credentials = f"{safe_user}:{safe_password}" if safe_password else safe_user
    return f"postgresql://{credentials}@{host}:{port}/{safe_database}"


def _build_connect_args(database_url: str) -> Dict[str, object]:
    """Configure SQLAlchemy connect arguments depending on the backend."""

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    if database_url.startswith("postgresql"):
        # Ensure psycopg2 interprets all identifiers using UTF-8.
        return {"options": "-c client_encoding=UTF8"}
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
