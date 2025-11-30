from database import run_query
from passlib.hash import bcrypt
from psycopg2.errors import UniqueViolation


def create_user(idUser: str, username: str, password: str, tipo: str):
    """Crea un usuario nuevo en la base de datos."""

    # Hash seguro de la contraseña
    hashed_pass = bcrypt.hash(password)

    query = """
        INSERT INTO userp (idUser, username, password, type)
        VALUES (%s, %s, %s, %s)
    """

    try:
        run_query(query, (idUser, username, hashed_pass, tipo))
        return {"ok": f"Usuario {username} creado correctamente."}

    except UniqueViolation:
        return {"error": "El ID de usuario ya existe."}
    except Exception as e:
        return {"error": str(e)}


def autenticate_user(username: str, password: str):
    """Verifica si un usuario existe y la contraseña es válida."""
    result = run_query(
        "SELECT * FROM userp WHERE username = %s", (username,), fetch=True
    )
    if not result:
        return {"error": "Usuario no encontrado."}

    user = result[0]
    if bcrypt.verify(password, user[2]):
        return {"ok": f"Bienvenido {username}"}
    else:
        return {"error": "Contraseña incorrecta."}
