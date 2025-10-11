from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date, time, timedelta

# -------------------
# USERS
# -------------------
class UserBase(BaseModel):
    name: str
    lastname: str
    email: EmailStr
    job: Optional[str] = None

class UserCreate(UserBase):
    password: str   # cuando se crea se envía en texto plano, luego se encripta

class UserResponse(UserBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# TYPE_TAG
# -------------------
class TypeTagBase(BaseModel):
    name: str

class TypeTagCreate(TypeTagBase):
    pass

class TypeTagResponse(TypeTagBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# TAGS
# -------------------
class TagBase(BaseModel):
    tag_code: str
    id_type_tag: int
    id_users: int

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# HEADQUARTERS
# -------------------
class HeadquartersBase(BaseModel):
    name: str

class HeadquartersCreate(HeadquartersBase):
    pass

class HeadquartersResponse(HeadquartersBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# STATUS_BAHIA
# -------------------
class StatusBahiaBase(BaseModel):
    name: str

class StatusBahiaCreate(StatusBahiaBase):
    pass

class StatusBahiaResponse(StatusBahiaBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# BAHIAS
# -------------------
class BahiaBase(BaseModel):
    name: str
    id_status_bahia: int
    id_headquarters: int
    module_loto_code: str | None = None
    module_loto_status: str | None = "offline"

class BahiaCreate(BahiaBase):
    pass

class BahiaResponse(BahiaBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# MAINTENANCE
# -------------------
class MaintenanceBase(BaseModel):
    name: str
    id_bahias: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str  

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceResponse(MaintenanceBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# PEOPLE IN MAINTENANCE
# -------------------
class PeopleInMaintenanceBase(BaseModel):
    id_users: int
    id_maintenance: int
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

class PeopleInMaintenanceCreate(PeopleInMaintenanceBase):
    pass

class PeopleInMaintenanceResponse(PeopleInMaintenanceBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# TYPES_ALERTS
# -------------------
class TypeAlertBase(BaseModel):
    name: str

class TypeAlertCreate(TypeAlertBase):
    pass

class TypeAlertResponse(TypeAlertBase):
    id: int
    class Config:
        orm_mode = True


# -------------------
# ALERTS
# -------------------
class AlertBase(BaseModel):
    alert_time: datetime
    id_maintenance: int
    id_people_in_maintenance: int
    id_types_alerts: int
    resolved: Optional[bool] = False
    resolved_at: Optional[datetime] = None

class AlertCreate(AlertBase):
    pass

# Para actualizar
class AlertUpdate(BaseModel):
    alert_time: Optional[time] = None
    id_maintenance: Optional[int] = None
    id_people_in_maintenance: Optional[int] = None
    id_types_alerts: Optional[int] = None
    resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None

class AlertResponse(AlertBase):
    id: int
    class Config:
        orm_mode = True
