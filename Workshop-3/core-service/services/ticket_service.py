"""
Logic to create a ticket
"""

from datetime import datetime
from sqlmodel import Session, select
from models import Ticket, Vehicle, LotSpace, Fee
from fastapi import HTTPException


def registrar_entrada(
    session: Session, ownerdoc: str, licenseplate: str, idFee: str, idUser: str
):
    # Verificar si ya tiene ticket abierto
    ticket_activo = session.exec(
        select(Ticket).where(Ticket.licenseplate == licenseplate, Ticket.exit == None)
    ).first()
    if ticket_activo:
        raise HTTPException(
            status_code=400, detail="El vehículo ya tiene un ticket activo."
        )

    vehiculo = session.get(Vehicle, licenseplate)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no registrado.")

    # Verificar disponibilidad
    espacio = session.exec(
        select(LotSpace).where(LotSpace.type == vehiculo.type)
    ).first()
    if not espacio or espacio.totalSpace <= 0:
        raise HTTPException(
            status_code=400,
            detail="No hay espacios disponibles para este tipo de vehículo.",
        )

    # Crear ticket
    nuevo_ticket = Ticket(
        ownerdoc=ownerdoc,
        entry=datetime.now(),
        licenseplate=licenseplate,
        idFee=idFee,
        idUser=idUser,
    )

    # Reducir espacio
    espacio.totalSpace -= 1
    session.add_all([nuevo_ticket, espacio])
    session.commit()
    session.refresh(nuevo_ticket)
    return nuevo_ticket
