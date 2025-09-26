# app/create_db.py
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import * # Importa todos los modelos para que Base los reconozca
from app.seed import seed_data
from sqlalchemy.exc import SQLAlchemyError


def reset_database():
    """
    Borra todas las tablas, las vuelve a crear e inserta los datos iniciales.
    """
    print("🔄 Reseteando la base de datos...")
    try:
        # Importante: Asegúrate que todos los modelos están importados antes de llamar a create_all
        print("    🔹 Borrando todas las tablas existentes...")
        Base.metadata.drop_all(bind=engine)
        print("    🔹 Creando todas las tablas nuevas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente.")

        # Iniciar una nueva sesión para sembrar los datos
        db: Session = SessionLocal()
        try:
            seed_data(db)
        finally:
            db.close()

    except SQLAlchemyError as e:
        print(f"❌ Error durante el reseteo de la base de datos: {e}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    reset_database()
