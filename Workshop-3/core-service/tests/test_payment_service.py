from services.payment_service import registrar_salida_y_pago
from services.ticket_service import registrar_entrada
from models import Vehicle, Fee, LotSpace, VehicleType, Ticket


def setup_payment_env(session):
    v = Vehicle(
        licenseplate="BBB222", type=VehicleType.CAR, dateRegistered="2024-01-01"
    )
    f = Fee(idFee="F1", descFee="Carros", type=VehicleType.CAR, priceFee=2000)
    l = LotSpace(idLotSpace="L1", type=VehicleType.CAR, totalSpace=5)
    session.add_all([v, f, l])
    session.commit()


def test_pago_exitosa(session):
    setup_payment_env(session)
    ticket = registrar_entrada(session, "999", "BBB222", "F1", "U1")
    pago = registrar_salida_y_pago(session, ticket.ticketid)
    assert pago.payment > 0
