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
    users = [
    models.User(name="Victor", lastname="Huatuco", email="victor@example.com", job="Ingeniero IoT", password_hash=bcrypt.hash("123456")),
    models.User(name="Francisco", lastname="Motta", email="francisco@example.com", job="Ingeniero de Mantenimiento", password_hash=bcrypt.hash("123456")),
    models.User(name="María", lastname="Gómez", email="maria.gomez@example.com", job="Supervisora de Seguridad", password_hash=bcrypt.hash("123456")),
    models.User(name="Juan", lastname="Pérez", email="juan.perez@example.com", job="Técnico Eléctrico", password_hash=bcrypt.hash("123456")),
    models.User(name="Lucía", lastname="Fernández", email="lucia.fernandez@example.com", job="Operadora de Maquinaria", password_hash=bcrypt.hash("123456")),
    models.User(name="Carlos", lastname="Ramírez", email="carlos.ramirez@example.com", job="Mecánico", password_hash=bcrypt.hash("123456")),
    models.User(name="Elena", lastname="Torres", email="elena.torres@example.com", job="Ingeniera de Seguridad", password_hash=bcrypt.hash("123456")),
    models.User(name="Diego", lastname="Vargas", email="diego.vargas@example.com", job="Electricista", password_hash=bcrypt.hash("123456")),
    models.User(name="Ana", lastname="Morales", email="ana.morales@example.com", job="Supervisora de Planta", password_hash=bcrypt.hash("123456")),
    models.User(name="José", lastname="Lopez", email="jose.lopez@example.com", job="Técnico Mecánico", password_hash=bcrypt.hash("123456")),
    models.User(name="Carmen", lastname="Castro", email="carmen.castro@example.com", job="Supervisora de Turno", password_hash=bcrypt.hash("123456")),
    models.User(name="Luis", lastname="Salazar", email="luis.salazar@example.com", job="Técnico de Mantenimiento", password_hash=bcrypt.hash("123456")),
    models.User(name="Rosa", lastname="Díaz", email="rosa.diaz@example.com", job="Ingeniera de Minas", password_hash=bcrypt.hash("123456")),
    models.User(name="Hugo", lastname="Cruz", email="hugo.cruz@example.com", job="Soldador", password_hash=bcrypt.hash("123456")),
    models.User(name="Patricia", lastname="Ramos", email="patricia.ramos@example.com", job="Supervisora de Seguridad", password_hash=bcrypt.hash("123456")),
    models.User(name="Fernando", lastname="García", email="fernando.garcia@example.com", job="Técnico Electrónico", password_hash=bcrypt.hash("123456")),
    models.User(name="Gabriela", lastname="Navarro", email="gabriela.navarro@example.com", job="Ingeniera Industrial", password_hash=bcrypt.hash("123456")),
    models.User(name="Andrés", lastname="Medina", email="andres.medina@example.com", job="Operador de Maquinaria", password_hash=bcrypt.hash("123456")),
    models.User(name="Claudia", lastname="Reyes", email="claudia.reyes@example.com", job="Supervisora de Producción", password_hash=bcrypt.hash("123456")),
    models.User(name="Ricardo", lastname="Ortiz", email="ricardo.ortiz@example.com", job="Técnico de Seguridad", password_hash=bcrypt.hash("123456")),
    ]
    db.add_all(users)
    db.commit()

    # -------------------
    # TYPE_TAG
    # -------------------
    type_tag_card = models.TypeTag(name="CARD")
    type_tag_loto = models.TypeTag(name="LOTO")
    db.add_all([type_tag_card, type_tag_loto])
    db.commit()

    # -------------------
    # TAGS
    # -------------------
    tags = [
    models.Tag(tag_code="192002151005100001", id_type_tag=type_tag_card.id, id_users=users[0].id),
    models.Tag(tag_code="192002151005200001", id_type_tag=type_tag_loto.id, id_users=users[0].id),

    models.Tag(tag_code="192002151005100002", id_type_tag=type_tag_card.id, id_users=users[1].id),
    models.Tag(tag_code="192002151005200002", id_type_tag=type_tag_loto.id, id_users=users[1].id),

    models.Tag(tag_code="192002151005100003", id_type_tag=type_tag_card.id, id_users=users[2].id),
    models.Tag(tag_code="192002151005200003", id_type_tag=type_tag_loto.id, id_users=users[2].id),

    models.Tag(tag_code="192002151005100004", id_type_tag=type_tag_card.id, id_users=users[3].id),
    models.Tag(tag_code="192002151005200004", id_type_tag=type_tag_loto.id, id_users=users[3].id),

    models.Tag(tag_code="192002151005100005", id_type_tag=type_tag_card.id, id_users=users[4].id),
    models.Tag(tag_code="192002151005200005", id_type_tag=type_tag_loto.id, id_users=users[4].id),

    models.Tag(tag_code="192002151005100006", id_type_tag=type_tag_card.id, id_users=users[5].id),
    models.Tag(tag_code="192002151005200006", id_type_tag=type_tag_loto.id, id_users=users[5].id),

    models.Tag(tag_code="192002151005100007", id_type_tag=type_tag_card.id, id_users=users[6].id),
    models.Tag(tag_code="192002151005200007", id_type_tag=type_tag_loto.id, id_users=users[6].id),

    models.Tag(tag_code="192002151005100008", id_type_tag=type_tag_card.id, id_users=users[7].id),
    models.Tag(tag_code="192002151005200008", id_type_tag=type_tag_loto.id, id_users=users[7].id),

    models.Tag(tag_code="192002151005100009", id_type_tag=type_tag_card.id, id_users=users[8].id),
    models.Tag(tag_code="192002151005200009", id_type_tag=type_tag_loto.id, id_users=users[8].id),

    models.Tag(tag_code="192002151005100010", id_type_tag=type_tag_card.id, id_users=users[9].id),
    models.Tag(tag_code="192002151005200010", id_type_tag=type_tag_loto.id, id_users=users[9].id),

    models.Tag(tag_code="192002151005100011", id_type_tag=type_tag_card.id, id_users=users[10].id),
    models.Tag(tag_code="192002151005200011", id_type_tag=type_tag_loto.id, id_users=users[10].id),

    models.Tag(tag_code="192002151005100012", id_type_tag=type_tag_card.id, id_users=users[11].id),
    models.Tag(tag_code="192002151005200012", id_type_tag=type_tag_loto.id, id_users=users[11].id),

    models.Tag(tag_code="192002151005100013", id_type_tag=type_tag_card.id, id_users=users[12].id),
    models.Tag(tag_code="192002151005200013", id_type_tag=type_tag_loto.id, id_users=users[12].id),

    models.Tag(tag_code="192002151005100014", id_type_tag=type_tag_card.id, id_users=users[13].id),
    models.Tag(tag_code="192002151005200014", id_type_tag=type_tag_loto.id, id_users=users[13].id),

    models.Tag(tag_code="192002151005100015", id_type_tag=type_tag_card.id, id_users=users[14].id),
    models.Tag(tag_code="192002151005200015", id_type_tag=type_tag_loto.id, id_users=users[14].id),

    models.Tag(tag_code="192002151005100016", id_type_tag=type_tag_card.id, id_users=users[15].id),
    models.Tag(tag_code="192002151005200016", id_type_tag=type_tag_loto.id, id_users=users[15].id),

    models.Tag(tag_code="192002151005100017", id_type_tag=type_tag_card.id, id_users=users[16].id),
    models.Tag(tag_code="192002151005200017", id_type_tag=type_tag_loto.id, id_users=users[16].id),

    models.Tag(tag_code="192002151005100018", id_type_tag=type_tag_card.id, id_users=users[17].id),
    models.Tag(tag_code="192002151005200018", id_type_tag=type_tag_loto.id, id_users=users[17].id),

    models.Tag(tag_code="192002151005100019", id_type_tag=type_tag_card.id, id_users=users[18].id),
    models.Tag(tag_code="192002151005200019", id_type_tag=type_tag_loto.id, id_users=users[18].id),

    models.Tag(tag_code="192002151005100020", id_type_tag=type_tag_card.id, id_users=users[19].id),
    models.Tag(tag_code="192002151005200020", id_type_tag=type_tag_loto.id, id_users=users[19].id),
    ]

    db.add_all(tags)
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
    status1 = models.StatusBahia(name="available")
    status2 = models.StatusBahia(name="inManteinance")
    status3 = models.StatusBahia(name="alert")
    status4 = models.StatusBahia(name="moduleDisconnected")
    db.add_all([status1, status2, status3, status4])
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
    # TYPES_ALERTS
    # -------------------
    alert_type1 = models.TypeAlert(name="Ingreso sin bloqueo de candado")
    alert_type2 = models.TypeAlert(name="Emergencia médica")
    db.add_all([alert_type1, alert_type2])
    db.commit()


    print("✅ Seed completado con éxito.")
