"""Database utilities for the FastAPI core service."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from typing import Dict
from urllib.parse import quote, unquote

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ArgumentError

load_dotenv()


def _quote_component(value: str | None, *, safe: str = "") -> str | None:
    """Return a percent-encoded version of a URL component."""

    if value is None:
        return None
    # Normalise any pre-existing escapes before applying percent-encoding.
    return quote(unquote(value), safe=safe)


def _build_query_string(query: Mapping[str, object]) -> str:
    """Serialise a SQLAlchemy query mapping using percent-encoding."""

    if not query:
        return ""

    segments: list[str] = []
    for raw_key, raw_value in query.items():
        key = quote(unquote(str(raw_key)), safe="")

        values: Sequence[object]
        if isinstance(raw_value, Sequence) and not isinstance(raw_value, (str, bytes)):
            values = raw_value
        else:
            values = (raw_value,)

        for value in values:
            text = "" if value is None else str(value)
            encoded = quote(unquote(text), safe="")
            segments.append(f"{key}={encoded}")

    return "?" + "&".join(segments)


def _render_postgres_url(url: URL) -> str:
    """Render a PostgreSQL URL ensuring credentials are ASCII safe."""

    username = _quote_component(url.username)
    password = _quote_component(url.password)
    database = _quote_component(url.database)

    auth = ""
    if username is not None:
        auth = username
        if password is not None:
            auth = f"{auth}:{password}"
        auth += "@"

    host = url.host or ""
    if host:
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        auth += host

    if url.port is not None:
        auth += f":{url.port}"

    path = f"/{database}" if database is not None else ""
    query = _build_query_string(url.query)

    return f"{url.drivername}://{auth}{path}{query}"


def _sanitize_database_url(database_url: str) -> str:
    """Percent-encode credentials and database names when needed."""

    try:
        url = make_url(database_url)
    except ArgumentError:
        return database_url

    if not url.drivername.startswith("postgres"):
        return database_url

    return _render_postgres_url(url)


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
    try:
        numeric_port = int(port)
    except (TypeError, ValueError):
        numeric_port = None

    url = URL.create(
        "postgresql",
        username=user,
        password=password,
        host=host,
        port=numeric_port,
        database=database,
    )
    return _render_postgres_url(url)


def _build_connect_args(database_url: str) -> Dict[str, object]:
    """Configure SQLAlchemy connect arguments depending on the backend."""

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    if database_url.startswith("postgres"):
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
