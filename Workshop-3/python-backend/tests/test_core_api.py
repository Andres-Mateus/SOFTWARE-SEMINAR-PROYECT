"""End-to-end tests for the FastAPI core service."""

from __future__ import annotations

from typing import Iterable

import pytest


def _find_slot(slots: Iterable[dict], code: str) -> dict:
    for slot in slots:
        if slot["code"] == code:
            return slot
    raise AssertionError(f"Slot {code} not found in response: {slots}")


@pytest.mark.parametrize("plate", ["ABC123", "XYZ789"])
def test_entry_exit_flow_updates_stats_and_slots(client, plate):
    entry_response = client.post("/api/core/entries", json={"plate": plate})
    assert entry_response.status_code == 201, entry_response.text
    entry_data = entry_response.json()
    assert entry_data["plate"] == plate
    assert entry_data["slot_code"], "Slot code should be returned"

    slots_response = client.get("/api/core/slots")
    assert slots_response.status_code == 200
    slot = _find_slot(slots_response.json(), entry_data["slot_code"])
    assert slot["occupied"] is True
    assert slot["plate"] == plate

    stats_response = client.get("/api/core/stats/overview")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["occupied"] >= 1
    assert stats["activeVehicles"] >= 1

    exit_response = client.post("/api/core/exits", json={"plate": plate})
    assert exit_response.status_code == 200, exit_response.text
    exit_data = exit_response.json()
    assert exit_data["plate"] == plate
    assert exit_data["minutes"] >= 1
    assert exit_data["amount"] > 0

    slots_after = client.get("/api/core/slots").json()
    slot_after = _find_slot(slots_after, entry_data["slot_code"])
    assert slot_after["occupied"] is False
    assert slot_after["plate"] is None


def test_sessions_endpoint_returns_recent_activity(client):
    plate = "SESSION1"
    client.post("/api/core/entries", json={"plate": plate})
    client.post("/api/core/exits", json={"plate": plate})

    sessions_response = client.get("/api/core/sessions?limit=5&order=desc")
    assert sessions_response.status_code == 200
    payload = sessions_response.json()
    assert "items" in payload
    assert payload["items"], "Sessions list should not be empty"
    latest = payload["items"][0]
    assert latest["plate"] == plate
    assert latest["check_out_at"] is not None
