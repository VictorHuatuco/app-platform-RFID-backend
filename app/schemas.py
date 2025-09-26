from pydantic import BaseModel
from datetime import date, time
from typing import Literal, Optional

# BusCompany Schema
class BusCompanyBase(BaseModel):
    bus_company: str

class BusCompanyCreate(BusCompanyBase):
    pass

class BusCompany(BusCompanyBase):
    id: int

    class Config:
        from_attributes = True

# Destination Schema
class DestinationBase(BaseModel):
    destination: str

class DestinationCreate(DestinationBase):
    pass

class Destination(DestinationBase):
    id: int

    class Config:
        from_attributes = True

# BoardingGate Schema
class BoardingGateBase(BaseModel):
    boarding_gate: str

class BoardingGateCreate(BoardingGateBase):
    pass

class BoardingGate(BoardingGateBase):
    id: int

    class Config:
        from_attributes = True

# Travel Schema (Se define antes de Announcement)
class TravelBase(BaseModel):
    id_bus_companies: int
    id_destinations: int
    departure_time: time
    plate: str

class TravelCreate(TravelBase):
    pass

class TravelUpdate(BaseModel):
    id_bus_companies: Optional[int] = None
    id_destinations: Optional[int] = None
    departure_time: Optional[time] = None
    plate: Optional[str] = None

class Travel(TravelBase):
    id: int
    bus_company: BusCompany  # Relación con BusCompany
    destination: Destination  # Relación con Destination

    class Config:
        from_attributes = True

# Announcement Schema
class AnnouncementBase(BaseModel):
    id_travels: int
    id_boarding_gates: Optional[int]
    id_users: int
    date_announcements: date
    status: bool
    observation: Literal["delayed", "canceled", "arrived"]

class AnnouncementCreate(AnnouncementBase):
    pass

class Announcement(AnnouncementBase):
    id: int
    travel: Travel
    boarding_gate: Optional[BoardingGate]  

    class Config:
        from_attributes = True

# User Schema
class UserBase(BaseModel):
    name: str
    email: str
    password: str
    id_terminals: int

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Terminal Schema
class TerminalBase(BaseModel):
    name: str
    city: str

class TerminalCreate(TerminalBase):
    pass

class Terminal(TerminalBase):
    id: int

    class Config:
        from_attributes = True

# Schema para Video existente
class VideoBase(BaseModel):
    filename: str
    title: Optional[str]
    description: Optional[str]
    order: int

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int

    class Config:
        orm_mode = True

# Schema para actualizar el orden de un video
class VideoOrderUpdate(BaseModel):
    id: int
    order: int