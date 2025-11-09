from sqlmodel import Session, select
from models import LotSpace


def obtener_disponibilidad(session: Session):
    return session.exec(select(LotSpace)).all()


def actualizar_capacidad(session: Session, tipo: str, cantidad: int):
    espacio = session.exec(select(LotSpace).where(LotSpace.type == tipo)).first()
    if espacio:
        espacio.totalSpace = cantidad
        session.add(espacio)
        session.commit()
        session.refresh(espacio)
        return espacio
    return None
