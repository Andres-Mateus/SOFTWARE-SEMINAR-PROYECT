from contextlib import contextmanager
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://admon:admon@localhost:5432/parking",
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def build_engine():
    # 1) URL de entorno si existe
    env_url = os.getenv("DATABASE_URL")

    # 2) Lista ordenada de intentos
    candidates = [u for u in [env_url, DEFAULT_PRIMARY, DEFAULT_SECONDARY, DEFAULT_SQLITE] if u]

    last_error = None
    for url in candidates:
        try:
            engine = create_engine(url, echo=False, future=True)
            # test conexión temprana
            with engine.connect() as conn:
                pass
            print(f"[DB] Using DATABASE_URL: {url}")
            return engine
        except Exception as exc:
            last_error = exc
            print(f"[DB] Failed DATABASE_URL: {url} -> {type(exc).__name__}")

    # Si nada funciona, explota con un error entendible
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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
