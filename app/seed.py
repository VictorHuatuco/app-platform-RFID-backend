# app/seed.py
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.database import SessionLocal
from app import models
from passlib.hash import bcrypt
from datetime import datetime, timedelta

def reset_sequences(db: Session):
    db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE type_tag_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE tags_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE headquarters_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE status_bahia_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE bahias_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE maintenance_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE people_in_maintenance_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE types_alerts_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE alerts_id_seq RESTART WITH 1;"))
    db.commit()


def seed_data(db: Session):
    # -------------------
    # ELIMINAR DATOS EXISTENTES
    # -------------------
    db.query(models.Alert).delete()
    db.query(models.PeopleInMaintenance).delete()
    db.query(models.Maintenance).delete()
    db.query(models.Bahia).delete()
    db.query(models.StatusBahia).delete()
    db.query(models.Headquarters).delete()
    db.query(models.Tag).delete()
    db.query(models.TypeTag).delete()
    db.query(models.TypeAlert).delete()
    db.query(models.User).delete()
    db.commit()

    reset_sequences(db)

    # -------------------
    # USERS
    # -------------------
    user1 = models.User(name="Victor", lastname="Huatuco", email="victor@example.com", job="Ingeniero IoT", password_hash=bcrypt.hash("123456"))
    user2 = models.User(name="Francisco", lastname="Motta", email="francisco@example.com", job="Ingeniero De Mantenimiento", password_hash=bcrypt.hash("123456"))
    db.add_all([user1, user2])
    db.commit()

    # -------------------
    # TYPE_TAG
    # -------------------
    type_tag1 = models.TypeTag(name="CARD")
    type_tag2 = models.TypeTag(name="LOTO")
    db.add_all([type_tag1, type_tag2])
    db.commit()

    # -------------------
    # TAGS
    # -------------------
    tag1 = models.Tag(tag_code="192002151005102510", id_type_tag=type_tag1.id, id_users=user1.id)
    tag2 = models.Tag(tag_code="192002151005102511", id_type_tag=type_tag2.id, id_users=user2.id)
    db.add_all([tag1, tag2])
    db.commit()

    # -------------------
    # HEADQUARTERS
    # -------------------
    hq1 = models.Headquarters(name="Mina Central")
    hq2 = models.Headquarters(name="Planta Sur")
    db.add_all([hq1, hq2])
    db.commit()

    # -------------------
    # STATUS_BAHIA
    # -------------------
    status1 = models.StatusBahia(name="Disponible")
    status2 = models.StatusBahia(name="En mantenimiento")
    db.add_all([status1, status2])
    db.commit()

    # -------------------
    # BAHIAS
    # -------------------
    bahia1 = models.Bahia(name="Bahía 1", id_status_bahia=status1.id, id_headquarters=hq1.id, module_loto_code = "LOTO-RFID-V1-A01")
    bahia2 = models.Bahia(name="Bahía 2", id_status_bahia=status2.id, id_headquarters=hq1.id, module_loto_code = "LOTO-RFID-V1-A02")
    bahia3 = models.Bahia(name="Bahía 3", id_status_bahia=status1.id, id_headquarters=hq1.id, module_loto_code = "LOTO-RFID-V1-A03")
    bahia4 = models.Bahia(name="Bahía 4", id_status_bahia=status1.id, id_headquarters=hq1.id, module_loto_code = "LOTO-RFID-V1-A04")
    bahia5 = models.Bahia(name="Bahía 5", id_status_bahia=status1.id, id_headquarters=hq1.id, module_loto_code = "LOTO-RFID-V1-A05")
    bahia6 = models.Bahia(name="Bahía 6", id_status_bahia=status1.id, id_headquarters=hq1.id, module_loto_code = "LOTO-RFID-V1-A06")
    db.add_all([bahia1, bahia2, bahia3, bahia4, bahia5, bahia6])
    db.commit()

    # -------------------
    # MAINTENANCE
    # -------------------
    maint1 = models.Maintenance(name="Cambio de motor", id_bahias=bahia1.id, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
    maint2 = models.Maintenance(name="Revisión de válvula", id_bahias=bahia2.id, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=3))
    db.add_all([maint1, maint2])
    db.commit()

    # -------------------
    # PEOPLE IN MAINTENANCE
    # -------------------
    pim1 = models.PeopleInMaintenance(id_users=user1.id, id_maintenance=maint1.id, entry_time=datetime.now())
    pim2 = models.PeopleInMaintenance(id_users=user2.id, id_maintenance=maint2.id, entry_time=datetime.now())
    db.add_all([pim1, pim2])
    db.commit()

    # -------------------
    # TYPES_ALERTS
    # -------------------
    alert_type1 = models.TypeAlert(name="Acceso no autorizado")
    alert_type2 = models.TypeAlert(name="Emergencia médica")
    db.add_all([alert_type1, alert_type2])
    db.commit()

    # -------------------
    # ALERTS
    # -------------------
    alert1 = models.Alert(alert_time=datetime.now().time(), id_maintenance=maint1.id, id_people_in_maintenance=pim1.id, id_types_alerts=alert_type1.id, resolved=False)
    alert2 = models.Alert(alert_time=datetime.now().time(), id_maintenance=maint2.id, id_people_in_maintenance=pim2.id, id_types_alerts=alert_type2.id, resolved=True, resolved_at=datetime.now())
    db.add_all([alert1, alert2])
    db.commit()

    print("✅ Seed completado con éxito.")
