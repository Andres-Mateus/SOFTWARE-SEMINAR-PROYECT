import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import run_query
import pytest
from services.vehicle_services import register_vehicle


@pytest.fixture(scope="module", autouse=True)
def limpiar_tabla():
    run_query("DELETE FROM vehicle")
    yield
    run_query("DELETE FROM vehicle")


def test_register_car():
    r = register_vehicle("AAA001", "CAR")
    assert "ok" in r


def test_create_vehicle_duplicated():
    register_vehicle("AAA002", "MOTORCYCLE")
    res = register_vehicle("AAA002", "MOTORCYCLE")
    assert "error" in res
