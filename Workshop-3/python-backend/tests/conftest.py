"""Shared pytest fixtures for FastAPI integration tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from database import get_session, seed_defaults
from main import app


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_defaults(session)
    yield engine


@pytest.fixture()
def client(test_engine):
    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_session, None)
