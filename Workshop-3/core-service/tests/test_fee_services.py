import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from services.fee_services import create_fee, get_fee
from database import run_query


@pytest.fixture(scope="module", autouse=True)
def limpiar_tabla_fee():
    """Limpia la tabla fee antes y después de las pruebas"""
    run_query("DELETE FROM fee")
    yield
    run_query("DELETE FROM fee")


def test_crear_fee_exitosamente():
    res = create_fee("F001", "Tarifa carro", "CAR", 3000)
    assert "ok" in res
    assert "F001" in res["ok"]


def test_crear_fee_duplicada():
    # Primera creación
    create_fee("F002", "Tarifa moto", "MOTORCYCLE", 2000)
    # Intento duplicado debe fallar
    with pytest.raises(Exception):
        create_fee("F002", "Tarifa duplicada", "CAR", 5000)


def test_get_fee_existente():
    create_fee("F003", "Tarifa camion", "TRUCK", 5000)
    fee = get_fee("F003")
    assert fee[0] == "F003"
    assert fee[2] == "TRUCK"


def test_get_fee_inexistente():
    fee = get_fee("NOEXISTE")
    assert "error" in fee
    assert "doesn't exist" in fee["error"]
