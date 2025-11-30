import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import run_query
import pytest
from services.user_services import create_user, autenticate_user


@pytest.fixture(scope="module", autouse=True)
def limpiar_tabla():
    run_query("DELETE FROM userp")
    yield
    run_query("DELETE FROM userp")


def test_create_user():
    r = create_user("U001", "juan", "clave123", "HUMAN")
    assert "ok" in r


def test_create_user_duplicated():
    create_user("U002", "ana", "clave123", "MACHINE")
    res = create_user("U002", "ana", "clave123", "MACHINE")
    assert "error" in res


def test_autenticacion_exitosa():
    create_user("U003", "pedro", "1234", "HUMAN")
    res = autenticate_user("pedro", "1234")
    assert "ok" in res


def test_autenticacion_incorrecta():
    create_user("U004", "luis", "1234", "HUMAN")
    res = autenticate_user("luis", "mala")
    assert "error" in res
