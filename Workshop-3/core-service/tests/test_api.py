import os
import tempfile
from datetime import datetime, timedelta

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Configure database before importing application modules
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.NamedTemporaryFile(delete=False).name

from database import Base, engine, get_session  # noqa: E402
from main import app  # noqa: E402
from models import ParkingSession, Slot  # noqa: E402
from services.parking_service import RATE_PER_MINUTE, ensure_slots  # noqa: E402


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        ensure_slots(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_stats_overview_contains_expected_keys(client):
    response = client.get("/api/core/stats/overview")
    assert response.status_code == 200
    data = response.json()

    expected_keys = {
        "occupied",
        "free",
        "activeVehicles",
        "active_sessions",
        "occupancyPercent",
        "occupancy_percent",
        "currentRatePerMinute",
        "rate_per_minute",
        "rate_per_hour",
    }
    assert expected_keys.issubset(data.keys())
    assert isinstance(data["occupied"], int)
    assert isinstance(data["free"], int)


def test_slots_return_occupied_state_matches_plate(client):
    entry_resp = client.post("/api/core/entries", json={"plate": "ABC-123"})
    assert entry_resp.status_code == 200

    resp = client.get("/api/core/slots")
    assert resp.status_code == 200
    slots = resp.json()
    assert isinstance(slots, list)
    assert len(slots) > 0

    for slot in slots:
        if slot["occupied"]:
            assert slot["plate"] is not None
        else:
            assert slot["plate"] is None


def test_sessions_respect_limit_and_order(client):
    with get_session() as session:
        slot = session.execute(select(Slot).order_by(Slot.code)).scalars().first()
        moments = [
            datetime.now() - timedelta(minutes=10),
            datetime.now() - timedelta(minutes=5),
            datetime.now() - timedelta(minutes=1),
        ]
        plates = ["AAA-111", "BBB-222", "CCC-333"]
        for plate, ts in zip(plates, moments):
            session.add(ParkingSession(plate=plate.replace("-", ""), slot=slot, check_in_at=ts))

    resp_desc = client.get("/api/core/sessions", params={"limit": 2, "order": "desc"})
    assert resp_desc.status_code == 200
    sessions_desc = resp_desc.json()
    assert len(sessions_desc) == 2
    assert sessions_desc[0]["check_in"] >= sessions_desc[1]["check_in"]

    resp_asc = client.get("/api/core/sessions", params={"limit": 2, "order": "asc"})
    assert resp_asc.status_code == 200
    sessions_asc = resp_asc.json()
    assert len(sessions_asc) == 2
    assert sessions_asc[0]["check_in"] <= sessions_asc[1]["check_in"]


def test_entry_success_and_slot_occupied(client):
    response = client.post("/api/core/entries", json={"plate": "XYZ-789"})
    assert response.status_code == 200
    data = response.json()
    assert data["plate"] == "XYZ-789"
    assert data["slot_code"]

    with get_session() as session:
        slot = session.execute(select(Slot).where(Slot.code == data["slot_code"])).scalar_one()
        assert slot.occupied is True


def test_entry_rejects_invalid_plate(client):
    response = client.post("/api/core/entries", json={"plate": "bad-plate"})
    assert response.status_code == 400
    assert "Invalid plate format" in response.json()["detail"]


def test_exit_success_returns_amount_and_frees_slot(client):
    entry = client.post("/api/core/entries", json={"plate": "LMN-456"})
    assert entry.status_code == 200
    slot_code = entry.json()["slot_code"]

    exit_resp = client.post("/api/core/exits", json={"plate": "LMN-456"})
    assert exit_resp.status_code == 200
    data = exit_resp.json()
    assert data["minutes"] >= 1
    assert data["amount"] >= RATE_PER_MINUTE
    assert data["slot_code"] == slot_code

    slots = client.get("/api/core/slots").json()
    freed = next(item for item in slots if item["code"] == slot_code)
    assert freed["occupied"] is False
    assert freed["plate"] is None


def test_exit_returns_not_found_when_no_session(client):
    response = client.post("/api/core/exits", json={"plate": "NOP-321"})
    assert response.status_code == 404
    assert "Active session not found" in response.json()["detail"]
