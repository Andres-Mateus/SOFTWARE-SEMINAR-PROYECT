from services.lot_service import obtener_disponibilidad, actualizar_capacidad
from models import LotSpace, VehicleType


def test_actualizar_y_obtener_lotes(session):
    espacio = LotSpace(idLotSpace="A1", type=VehicleType.CAR, totalSpace=10)
    session.add(espacio)
    session.commit()

    actualizar_capacidad(session, VehicleType.CAR, 5)
    lotes = obtener_disponibilidad(session)
    assert lotes[0].totalSpace == 5
