"""
Logic to do a ticketpayment
"""

from datetime import datetime
from sqlmodel import Session
from models import Ticket, Payment, Fee, LotSpace
from fastapi import HTTPException


def registrar_salida_y_pago(session: Session, ticketid: int):
    ticket = session.get(Ticket, ticketid)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    if ticket.exit:
        raise HTTPException(status_code=400, detail="El ticket ya fue cerrado.")

    tarifa = session.get(Fee, ticket.idFee)
    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada.")

    # Calcular duración exacta
    ticket.exit = datetime.now()
    duracion = (ticket.exit - ticket.entry).total_seconds() / 3600  # horas
    duracion = max(1, round(duracion, 2))  # mínimo 1h
    total = tarifa.priceFee * duracion

    pago = Payment(ticketid=ticket.ticketid, datepayment=datetime.now(), payment=total)

    # Liberar espacio
    espacio = session.exec(
        f"UPDATE lotspace SET totalSpace = totalSpace + 1 WHERE type = '{tarifa.type}'"
    )

    session.add_all([ticket, pago])
    session.commit()
    session.refresh(pago)
    return pago
