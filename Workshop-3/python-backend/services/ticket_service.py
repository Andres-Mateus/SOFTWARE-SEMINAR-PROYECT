"""Ticket operations supporting vehicle entries and exits."""

from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from models import Fee, LotSpace, Ticket, Vehicle


def _find_available_slot(session: Session, vehicle: Vehicle) -> LotSpace:
    slot = session.exec(
        select(LotSpace).where(
            LotSpace.type == vehicle.type, LotSpace.current_plate.is_(None)
        )
    ).first()
    if not slot:
        raise HTTPException(
            status_code=400,
            detail="No available slots for the requested vehicle type.",
        )
    return slot


def registrar_entrada(
    session: Session,
    owner_document: str,
    license_plate: str,
    fee_id: str,
    user_id: str,
) -> Ticket:
    active_ticket = session.exec(
        select(Ticket).where(
            Ticket.licenseplate == license_plate, Ticket.exit.is_(None)
        )
    ).first()
    if active_ticket:
        raise HTTPException(
            status_code=400, detail="The vehicle already has an active ticket."
        )

    vehicle = session.get(Vehicle, license_plate)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not registered.")

    fee = session.get(Fee, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Pricing configuration not found.")

    slot = _find_available_slot(session, vehicle)

    ticket = Ticket(
        ownerdoc=owner_document,
        entry=datetime.utcnow(),
        licenseplate=license_plate,
        idfee=fee.idfee,
        iduser=user_id,
        slotcode=slot.idLotSpace,
    )

    slot.current_plate = license_plate

    session.add_all([ticket, slot])
    session.commit()
    session.refresh(ticket)
    return ticket
