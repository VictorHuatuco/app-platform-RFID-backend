from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas
from app.schemas import TravelCreate, Travel, BoardingGate
import asyncio

# Importa la función de broadcast desde el módulo de Socket.IO
from app.routers import socketio_announcements

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.post("/")
def create_announcement(announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db)):
    print("📩 Recibido:", announcement.dict())  # Verifica los datos recibidos
    db_announcement = models.Announcements(**announcement.dict())
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)

     # Dispara la emisión en segundo plano
    try:
        asyncio.get_running_loop().create_task(socketio_announcements.broadcast_announcements())
    except RuntimeError:
        # En caso de no haber event loop activo (poco probable con Uvicorn)
        asyncio.run(socketio_announcements.broadcast_announcements())
    
    return {"message": "success", "data": db_announcement}

@router.get("/{announcement_id}", response_model=schemas.Announcement)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    announcement = db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first()
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement

@router.get("/", response_model=list[schemas.Announcement])
def list_announcements(db: Session = Depends(get_db)):
    announcements = (
        db.query(models.Announcements)
        .filter(models.Announcements.status == True) 
        .options(
            joinedload(models.Announcements.travel).joinedload(models.Travels.bus_company),
            joinedload(models.Announcements.travel).joinedload(models.Travels.destination),
            joinedload(models.Announcements.boarding_gate),
        )
        .order_by(models.Announcements.id)
        .all()
    )
    return announcements

@router.put("/{announcement_id}", response_model=schemas.Announcement)
def update_announcement(announcement_id: int, announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db)):
    db_announcement = db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first()
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    for key, value in announcement.dict().items():
        setattr(db_announcement, key, value)
    db.commit()
    db.refresh(db_announcement)

     # Dispara la emisión en segundo plano
    try:
        asyncio.get_running_loop().create_task(socketio_announcements.broadcast_announcements())
    except RuntimeError:
        asyncio.run(socketio_announcements.broadcast_announcements())

    return db_announcement

@router.patch("/{announcement_id}/status", response_model=schemas.Announcement)
def update_announcement_status(
    announcement_id: int, 
    status: bool, 
    db: Session = Depends(get_db)
):
    db_announcement = db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first()
    
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    db_announcement.status = status
    db.commit()
    db.refresh(db_announcement)

    # Dispara la emisión en segundo plano
    try:
        asyncio.get_running_loop().create_task(socketio_announcements.broadcast_announcements())
    except RuntimeError:
        asyncio.run(socketio_announcements.broadcast_announcements())
    
    return db_announcement


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    db_announcement = db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first()
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(db_announcement)
    db.commit()
    return {"message": "Announcement deleted"}
