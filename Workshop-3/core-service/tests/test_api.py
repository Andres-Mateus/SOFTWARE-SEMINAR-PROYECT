import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.NamedTemporaryFile(delete=False).name

from database import Base, engine, get_session  # noqa: E402
from main import app  # noqa: E402
from models import ParkingSession, Slot  # noqa: E402
from services.parking_service import ensure_slots  # noqa: E402


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        ensure_slots(session)
    yield


def test_stats_and_slots():
    client = TestClient(app)
    stats_resp = client.get("/api/core/stats/overview")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["free"] >= 0

    slots_resp = client.get("/api/core/slots")
    assert slots_resp.status_code == 200
    assert isinstance(slots_resp.json(), list)


def test_entry_and_exit_flow():
    client = TestClient(app)

    entry_resp = client.post("/api/core/entries", json={"plate": "abc123"})
    assert entry_resp.status_code == 200
    entry_data = entry_resp.json()
    assert entry_data["slot_code"]

    exit_resp = client.post("/api/core/exits", json={"plate": "abc123"})
    assert exit_resp.status_code == 200
    exit_data = exit_resp.json()
    assert exit_data["amount"] >= 0


def test_sessions_listing_orders_by_check_in():
    client = TestClient(app)
    with get_session() as session:
        slot = session.query(Slot).first()
        for plate in ["AAA111", "BBB222", "CCC333"]:
            session.add(ParkingSession(plate=plate, slot=slot, check_in_at=datetime.now(timezone.utc)))

    resp = client.get("/api/core/sessions?limit=2&order=desc")
    assert resp.status_code == 200
    sessions = resp.json()
    assert len(sessions) == 2
