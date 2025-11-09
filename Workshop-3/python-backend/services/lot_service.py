"""Helpers to expose parking slot availability."""

from collections import defaultdict
from typing import Any, Dict, List

from sqlmodel import Session, select

from models import LotSpace


def obtener_disponibilidad(session: Session) -> List[Dict[str, Any]]:
    slots = session.exec(select(LotSpace)).all()
    return [
        {
            "code": slot.idLotSpace,
            "type": slot.type,
            "occupied": slot.current_plate is not None,
            "plate": slot.current_plate,
        }
        for slot in slots
    ]


def resumen_ocupacion(session: Session) -> Dict[str, Dict[str, int]]:
    summary: Dict[str, Dict[str, int]] = defaultdict(lambda: {"occupied": 0, "total": 0})
    for slot in session.exec(select(LotSpace)).all():
        summary[slot.type]["total"] += 1
        if slot.current_plate:
            summary[slot.type]["occupied"] += 1
    return summary
