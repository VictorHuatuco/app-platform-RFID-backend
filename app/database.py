import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Cargar variables de entorno
load_dotenv()

# Variables de entorno con valores por defecto
APP_DB_NAME = os.getenv("APP_DB_NAME", "mydatabase")
APP_DB_USER = os.getenv("APP_DB_USER", "user")
APP_DB_PASSWORD = os.getenv("APP_DB_PASSWORD", "password")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")

# URL de conexión a la base de datos
DATABASE_URL = (
    f"postgresql://{APP_DB_USER}:{APP_DB_PASSWORD}@{PG_HOST}:{PG_PORT}/{APP_DB_NAME}"
)

# Motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Pon True para ver las queries SQL en la consola
    future=True, # Usa la API moderna de SQLAlchemy 2.0
    pool_pre_ping=True,
)

# Creador de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    future=True,
)

# Base declarativa para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de BD (para FastAPI)
def get_db():
    """Generador de sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
