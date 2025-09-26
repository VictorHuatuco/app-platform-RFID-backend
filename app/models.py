from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    Time,
)
from sqlalchemy.orm import relationship
from .database import Base


# -------------------
# USERS
# -------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    job = Column(String, nullable=True)

    # relaciones
    tags = relationship("Tag", back_populates="user")
    people_in_maintenance = relationship(
        "PeopleInMaintenance", back_populates="user"
    )


# -------------------
# TYPE_TAG
# -------------------
class TypeTag(Base):
    __tablename__ = "type_tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    # relaciones
    tags = relationship("Tag", back_populates="type_tag")


# -------------------
# TAGS
# -------------------
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    tag_code = Column(String, unique=True, index=True)
    id_type_tag = Column(Integer, ForeignKey("type_tag.id"))
    id_users = Column(Integer, ForeignKey("users.id"))

    # relaciones
    type_tag = relationship("TypeTag", back_populates="tags")
    user = relationship("User", back_populates="tags")


# -------------------
# HEADQUARTERS
# -------------------
class Headquarters(Base):
    __tablename__ = "headquarters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    # relaciones
    bahias = relationship("Bahia", back_populates="headquarters")


# -------------------
# STATUS_BAHIA
# -------------------
class StatusBahia(Base):
    __tablename__ = "status_bahia"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    # relaciones
    bahias = relationship("Bahia", back_populates="status")


# -------------------
# BAHIAS
# -------------------
class Bahia(Base):
    __tablename__ = "bahias"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    id_status_bahia = Column(Integer, ForeignKey("status_bahia.id"))
    id_headquarters = Column(Integer, ForeignKey("headquarters.id"))
    module_loto_code = Column(String, unique=True, nullable=True)
    module_loto_status = Column(String, default="offline", nullable=False)

    # relaciones
    status = relationship("StatusBahia", back_populates="bahias")
    headquarters = relationship("Headquarters", back_populates="bahias")
    maintenances = relationship("Maintenance", back_populates="bahia")


# -------------------
# MAINTENANCE
# -------------------
class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    id_bahias = Column(Integer, ForeignKey("bahias.id"))
    start_time = Column(TIMESTAMP, nullable=True)
    end_time = Column(TIMESTAMP, nullable=True)

    # relaciones
    bahia = relationship("Bahia", back_populates="maintenances")
    people_in_maintenance = relationship(
        "PeopleInMaintenance", back_populates="maintenance"
    )
    alerts = relationship("Alert", back_populates="maintenance")


# -------------------
# PEOPLE IN MAINTENANCE
# -------------------
class PeopleInMaintenance(Base):
    __tablename__ = "people_in_maintenance"

    id = Column(Integer, primary_key=True, index=True)
    id_users = Column(Integer, ForeignKey("users.id"))
    id_maintenance = Column(Integer, ForeignKey("maintenance.id"))
    entry_time = Column(TIMESTAMP, nullable=True)
    exit_time = Column(TIMESTAMP, nullable=True)

    # relaciones
    user = relationship("User", back_populates="people_in_maintenance")
    maintenance = relationship(
        "Maintenance", back_populates="people_in_maintenance"
    )
    alerts = relationship("Alert", back_populates="people_in_maintenance")


# -------------------
# TYPES_ALERTS
# -------------------
class TypeAlert(Base):
    __tablename__ = "types_alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    # relaciones
    alerts = relationship("Alert", back_populates="type_alert")


# -------------------
# ALERTS
# -------------------
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_time = Column(Time, nullable=True)
    id_maintenance = Column(Integer, ForeignKey("maintenance.id"))
    id_people_in_maintenance = Column(
        Integer, ForeignKey("people_in_maintenance.id")
    )
    id_types_alerts = Column(Integer, ForeignKey("types_alerts.id"))
    resolved = Column(Boolean, default=False)
    resolved_at = Column(TIMESTAMP, nullable=True)  # <-- Corregido aquí

    # relaciones
    maintenance = relationship("Maintenance", back_populates="alerts")
    people_in_maintenance = relationship(
        "PeopleInMaintenance", back_populates="alerts"
    )
    type_alert = relationship("TypeAlert", back_populates="alerts")
