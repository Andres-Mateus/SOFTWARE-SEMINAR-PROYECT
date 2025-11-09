"""Vehicle helper operations used by the API layer."""

from datetime import datetime

from sqlmodel import Session

from models import Vehicle, VehicleType


def registrar_vehiculo(
    session: Session, licenseplate: str, vehicle_type: VehicleType
) -> Vehicle:
    existente = session.get(Vehicle, licenseplate)
    if existente:
        return existente

    nuevo = Vehicle(
        licenseplate=licenseplate,
        type=vehicle_type,
        dateregistered=datetime.utcnow(),
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo
