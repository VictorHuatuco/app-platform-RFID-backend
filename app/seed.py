from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.database import SessionLocal
from app import models

def reset_sequences(db: Session):
    db.execute(text("ALTER SEQUENCE terminals_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE bus_companies_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE destinations_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE boarding_gates_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE travels_id_seq RESTART WITH 1;"))
    db.execute(text("ALTER SEQUENCE announcements_id_seq RESTART WITH 1;"))
    db.commit()

def seed_data(db: Session):
    #Eliminar DAtos siu ya existe:
    db.query(models.Announcements).delete()
    db.query(models.Travels).delete()
    db.query(models.Users).delete()
    db.query(models.BoardingGates).delete()
    db.query(models.Destinations).delete()
    db.query(models.BusCompanies).delete()
    db.query(models.Terminals).delete()
    db.commit()

    # Resetear secuencias para que los IDs vuelvan a 1
    reset_sequences(db)
    
    # Crear terminales
    terminal1 = models.Terminals(name="Terminal Central", city="Lima")
    terminal2 = models.Terminals(name="Terminal Norte", city="Trujillo")
    db.add_all([terminal1, terminal2])
    db.commit()

    # Crear empresas de buses
    bus_company1 = models.BusCompanies(bus_company="Expreso Lima")
    bus_company2 = models.BusCompanies(bus_company="Transportes Andinos")
    bus_company3 = models.BusCompanies(bus_company="Perú Bus")
    bus_company4 = models.BusCompanies(bus_company="Cruz del Sur")
    bus_company5 = models.BusCompanies(bus_company="Ticllas")
    bus_company6 = models.BusCompanies(bus_company="Oropesa")
    db.add_all([bus_company1, bus_company2, bus_company3, bus_company4, bus_company5, bus_company6])
    db.commit()

    # Crear destinos
    destination1 = models.Destinations(destination="Arequipa")
    destination2 = models.Destinations(destination="Cusco")
    destination3 = models.Destinations(destination="Piura")
    destination4 = models.Destinations(destination="Tacna")
    destination5 = models.Destinations(destination="Chiclayo")
    destination6 = models.Destinations(destination="Iquitos")
    db.add_all([destination1, destination2, destination3, destination4, destination5, destination6])
    db.commit()

    # Crear puertas de embarque
    gate1 = models.BoardingGates(boarding_gate="Puerta 1")
    gate2 = models.BoardingGates(boarding_gate="Puerta 2")
    gate3 = models.BoardingGates(boarding_gate="Puerta 3")
    gate4 = models.BoardingGates(boarding_gate="Puerta 4")
    gate5 = models.BoardingGates(boarding_gate="Puerta 5")
    gate6 = models.BoardingGates(boarding_gate="Puerta 6")
    db.add_all([gate1, gate2, gate3, gate4, gate5, gate6])
    db.commit()

    # Crear usuarios
    user1 = models.Users(name="Juan Perez", email="juan@example.com", password="1234", id_terminals=terminal1.id)
    user2 = models.Users(name="Maria López", email="maria@example.com", password="5678", id_terminals=terminal2.id)
    user3 = models.Users(name="Carlos Ramos", email="carlos@example.com", password="abcd", id_terminals=terminal1.id)
    user4 = models.Users(name="Lucia Torres", email="lucia@example.com", password="efgh", id_terminals=terminal2.id)
    db.add_all([user1, user2, user3, user4])
    db.commit()

    # Crear viajes
    travel1 = models.Travels(id_bus_companies=bus_company1.id, id_destinations=destination1.id, departure_time="08:30:00", plate="ABC-123")
    travel2 = models.Travels(id_bus_companies=bus_company2.id, id_destinations=destination2.id, departure_time="14:15:00", plate="XYZ-789")
    travel3 = models.Travels(id_bus_companies=bus_company3.id, id_destinations=destination3.id, departure_time="10:15:00", plate="IBZ-243")
    travel4 = models.Travels(id_bus_companies=bus_company4.id, id_destinations=destination4.id, departure_time="16:15:00", plate="ABC-123")
    travel5 = models.Travels(id_bus_companies=bus_company5.id, id_destinations=destination5.id, departure_time="09:45:00", plate="DEF-456")
    travel6 = models.Travels(id_bus_companies=bus_company6.id, id_destinations=destination6.id, departure_time="18:00:00", plate="GHI-789")
    db.add_all([travel1, travel2, travel3, travel4, travel5, travel6])
    db.commit()


    # Crear anuncios
    announcement1 = models.Announcements(id_travels=travel1.id, id_boarding_gates=gate1.id, id_users=user1.id, date_announcements="2025-03-12",status= False , observation="delayed")
    announcement2 = models.Announcements(id_travels=travel2.id, id_boarding_gates= None, id_users=user2.id, date_announcements="2025-03-12",status= True , observation="canceled")
    announcement3 = models.Announcements(id_travels=travel3.id, id_boarding_gates=gate3.id, id_users=user3.id, date_announcements="2025-03-14",status= True , observation="arrived")
    announcement4 = models.Announcements(id_travels=travel4.id, id_boarding_gates=gate4.id, id_users=user4.id, date_announcements="2025-03-14",status= True , observation="delayed")
    announcement5 = models.Announcements(id_travels=travel5.id, id_boarding_gates=gate5.id, id_users=user1.id, date_announcements="2025-03-15",status= True , observation="arrived")
    announcement6 = models.Announcements(id_travels=travel6.id, id_boarding_gates= None, id_users=user2.id, date_announcements="2025-03-16",status= True , observation="canceled")
    db.add_all([announcement1, announcement2, announcement3, announcement4, announcement5, announcement6])
    db.commit()

    print("✅ Seed completado con éxito.")

if __name__ == "__main__":
    db = SessionLocal()
    seed_data(db)
    db.close()
