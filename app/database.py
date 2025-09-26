# app/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base

# Cargar variables de entorno
load_dotenv()

app_db_name = os.getenv("APP_DB_NAME")
app_db_user = os.getenv("APP_DB_USER")
app_db_password = os.getenv("APP_DB_PASSWORD")
pg_host = os.getenv("PG_HOST")
pg_port = os.getenv("PG_PORT")

DATABASE_URL = f"postgresql://{app_db_user}:{app_db_password}@{pg_host}:{pg_port}/{app_db_name}"

# Crear la conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Crea las tablas en la base de datos si no existen."""
    Base.metadata.create_all(engine)

# ✅ Agrega esta función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Tablas creadas correctamente.")
