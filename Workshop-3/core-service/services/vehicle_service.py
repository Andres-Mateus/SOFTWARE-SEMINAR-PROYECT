from sqlmodel import Session
from models import Vehicle
from datetime import datetime


def registrar_vehiculo(session: Session, licenseplate: str, type: str):
    existente = session.get(Vehicle, licenseplate)
    if existente:
        return existente
    nuevo = Vehicle(licenseplate=licenseplate, type=type, dateRegistered=datetime.now())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo
