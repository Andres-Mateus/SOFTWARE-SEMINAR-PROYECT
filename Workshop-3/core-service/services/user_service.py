"""
Logic to do a ticketpayment
"""

from sqlmodel import Session
from models import User
from fastapi import HTTPException
from passlib.hash import bcrypt


def crear_usuario(
    session: Session, idUser: str, username: str, password: str, type: str
):
    if session.get(User, idUser):
        raise HTTPException(status_code=400, detail="Usuario ya existe.")
    hashed = bcrypt.hash(password)
    user = User(idUser=idUser, username=username, password=hashed, type=type)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def autenticar(session: Session, username: str, password: str):
    user = session.query(User).filter(User.username == username).first()
    if not user or not bcrypt.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    return user
