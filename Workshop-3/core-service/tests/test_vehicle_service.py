from services.vehicle_service import registrar_vehiculo
from models import Vehicle


def test_registrar_vehiculo(session):
    vehiculo = registrar_vehiculo(session, "ABC123", "CAR")
    assert vehiculo.licenseplate == "ABC123"


def test_registrar_vehiculo_existente(session):
    registrar_vehiculo(session, "XYZ789", "BUS")
    v2 = registrar_vehiculo(session, "XYZ789", "BUS")
    assert v2.type == "BUS"
