from services.ticket_service import registrar_entrada
from models import Vehicle, Fee, LotSpace, VehicleType


def setup_ticket_env(session):
    v = Vehicle(
        licenseplate="AAA111", type=VehicleType.CAR, dateRegistered="2024-01-01"
    )
    f = Fee(idFee="F1", descFee="Carros", type=VehicleType.CAR, priceFee=2000)
    l = LotSpace(idLotSpace="L1", type=VehicleType.CAR, totalSpace=5)
    session.add_all([v, f, l])
    session.commit()


def test_registrar_entrada_exitoso(session):
    setup_ticket_env(session)
    ticket = registrar_entrada(session, "123", "AAA111", "F1", "U1")
    assert ticket.licenseplate == "AAA111"


def test_entrada_repetida(session):
    setup_ticket_env(session)
    registrar_entrada(session, "123", "AAA111", "F1", "U1")
    try:
        registrar_entrada(session, "123", "AAA111", "F1", "U1")
    except Exception as e:
        assert "activo" in str(e)
