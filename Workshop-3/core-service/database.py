"""
The script funcion is connect the PostgreSQL DB with the core-service
"""

from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

host = "localhost"
user = "admon"
password = "admon"
database = "parking"

DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{database}"
engine = create_engine(DATABASE_URL, echo=True)


# Función para inicializar las tablas
def init_db():
    SQLModel.metadata.create_all(engine)


# Función para obtener una sesión en FastAPI (usada en Depends)
def get_session():
    with Session(engine) as session:
        yield session
