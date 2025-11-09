from services.user_service import crear_usuario, autenticar
from fastapi import HTTPException


def test_crear_usuario(session):
    user = crear_usuario(session, "123", "juan", "clave", "HUMAN REGISTER")
    assert user.username == "juan"


def test_usuario_duplicado(session):
    crear_usuario(session, "123", "juan", "clave", "HUMAN REGISTER")
    try:
        crear_usuario(session, "123", "juan", "clave", "HUMAN REGISTER")
    except HTTPException as e:
        assert e.status_code == 400


def test_autenticacion_exitosa(session):
    crear_usuario(session, "123", "juan", "clave", "HUMAN REGISTER")
    user = autenticar(session, "juan", "clave")
    assert user.idUser == "123"


def test_autenticacion_fallida(session):
    crear_usuario(session, "123", "juan", "clave", "HUMAN REGISTER")
    try:
        autenticar(session, "juan", "mala")
    except Exception as e:
        assert "inválidas" in str(e)
