# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Conexión directa al servicio 'db' de Docker usando las credenciales del compose
DATABASE_URL = "postgresql://postgres:postgres@db:5432"

# El engine es el encargado de comunicarse directamente con Postgres
engine = create_engine(DATABASE_URL)

# Cada vez que necesites consultar la BD, usarás una instancia de SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta clase Base es de donde van a heredar tus objetos en models.py para convertirse en tablas
Base = declarative_base()

# Una función auxiliar (Dependency) que usarás en tus rutas de FastAPI para abrir/cerrar la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
