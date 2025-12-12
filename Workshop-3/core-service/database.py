from contextlib import contextmanager
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Default DB candidates (ASCII-safe) ---
DEFAULT_PRIMARY = "postgresql+psycopg2://admon:admon@localhost:5432/parking"
DEFAULT_SECONDARY = "postgresql+psycopg2://postgres:12345@localhost:5432/parking"
DEFAULT_SQLITE = "sqlite:///./parking.db"


def build_engine():
    env_url = os.getenv("DATABASE_URL")

    candidates = [
        u for u in [
            env_url,
            DEFAULT_PRIMARY,
            DEFAULT_SECONDARY,
            DEFAULT_SQLITE
        ]
        if u
    ]

    last_error = None
    for url in candidates:
        try:
            engine = create_engine(url, echo=False, future=True)
            # quick connectivity check
            with engine.connect():
                pass
            print(f"[DB] Using DATABASE_URL: {url}")
            return engine
        except Exception as exc:
            last_error = exc
            print(f"[DB] Failed DATABASE_URL: {url} -> {type(exc).__name__}")

    raise RuntimeError(f"No valid database configuration found. Last error: {last_error}")


engine = build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

Base = declarative_base()


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()