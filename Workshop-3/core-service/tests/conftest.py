import pytest
from sqlmodel import SQLModel, create_engine, Session
from models import *


@pytest.fixture(name="session")
def session_fixture():
    # Crear DB temporal en memoria
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
