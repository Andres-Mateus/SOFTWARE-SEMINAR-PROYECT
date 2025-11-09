"""Payment helpers to close tickets and compute totals."""

from datetime import datetime
from math import ceil
from typing import Tuple

from fastapi import HTTPException
from sqlmodel import Session

from models import Fee, LotSpace, Payment, Ticket


def registrar_salida_y_pago(session: Session, ticket_id: int) -> Tuple[Payment, int]:
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    if ticket.exit:
        raise HTTPException(status_code=400, detail="The ticket is already closed.")

    fee = session.get(Fee, ticket.idfee)
    if not fee:
        raise HTTPException(status_code=404, detail="Pricing configuration not found.")

    exit_time = datetime.utcnow()
    ticket.exit = exit_time

    duration_minutes = max(
        1, ceil((ticket.exit - ticket.entry).total_seconds() / 60)
    )
    total = round((fee.pricefee / 60) * duration_minutes, 2)

    payment = Payment(ticketid=ticket.ticketid, datepayment=exit_time, payment=total)

    slot: LotSpace | None = (
        session.get(LotSpace, ticket.slotcode) if ticket.slotcode else None
    )
    if slot:
        slot.current_plate = None
        session.add(slot)

    session.add_all([ticket, payment])
    session.commit()
    session.refresh(payment)
    return payment, duration_minutes
