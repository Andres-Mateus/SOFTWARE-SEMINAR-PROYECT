import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel, Session  # noqa: E402

from main import app  # noqa: E402
from database import engine, get_session  # noqa: E402


def override_get_session():
    with Session(engine) as session:
        yield session


def setup_module(module):
    SQLModel.metadata.create_all(engine)
    app.dependency_overrides[get_session] = override_get_session


def teardown_module(module):
    SQLModel.metadata.drop_all(engine)
    app.dependency_overrides.clear()


def test_create_and_list_user():
    client = TestClient(app)

    user_payload = {
        "idUser": "USR001",
        "username": "john.doe",
        "password": "secret",
        "type": "HUMAN REGISTER",
    }

    create_response = client.post("/api/core/users", json=user_payload)
    assert create_response.status_code == 200
    user_data = create_response.json()
    assert user_data["idUser"] == user_payload["idUser"]
    assert user_data["username"] == user_payload["username"]
    assert user_data["type"] == user_payload["type"]

    list_response = client.get("/api/core/users")
    assert list_response.status_code == 200
    users = list_response.json()
    assert len(users) == 1
    assert users[0]["idUser"] == user_payload["idUser"]
