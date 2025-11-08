"""
The script funtion is to create the basic crud functions to interact with db
"""

from sqlmodel import Session, select


def crear_registro(session: Session, modelo):
    session.add(modelo)
    session.commit()
    session.refresh(modelo)
    return modelo


def obtener_todos(session: Session, modelo_cls):
    return session.exec(select(modelo_cls)).all()


def obtener_por_id(session: Session, modelo_cls, id_):
    return session.get(modelo_cls, id_)


def actualizar_registro(session: Session, modelo_cls, id_, data: dict):
    registro = session.get(modelo_cls, id_)
    if not registro:
        return None
    for key, value in data.items():
        setattr(registro, key, value)
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro


def eliminar_registro(session: Session, modelo_cls, id_):
    registro = session.get(modelo_cls, id_)
    if not registro:
        return None
    session.delete(registro)
    session.commit()
    return registro
