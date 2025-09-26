#app/socketio_announcements.py
import socketio
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import engine
from app.models import Announcements, Travels
from app.schemas import Announcement as AnnouncementSchema
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import asyncio

# Configura Socket.IO para permitir el origen de tu frontend.
# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
# sio_app = socketio.ASGIApp(sio)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="http://localhost:4200")
# sio_app = socketio.ASGIApp(sio, socketio_path="/socket.io")
sio_app = socketio.ASGIApp(sio, socketio_path="/ws/announcements/socket.io")

router = APIRouter()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@sio.event
async def connect(sid, environ):
    print(f"Socket.IO: Cliente conectado: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Socket.IO: Cliente desconectado: {sid}")

async def broadcast_announcements():
    db = SessionLocal()
    try:
        # print("Obteniendo videos de la base de datos...")
        announcements = (
            db.query(Announcements)
            .filter(Announcements.status == True)
            .options(
                joinedload(Announcements.travel).joinedload(Travels.bus_company),
                joinedload(Announcements.travel).joinedload(Travels.destination),
                joinedload(Announcements.boarding_gate)
            )
            .order_by(Announcements.id)
            .all()
        )
        
        if not announcements:
            print("No se encontraron announcements en la base de datos.")
        # else:
        #     print(f"announcements obtenidos: {announcements}")
        

        data = [jsonable_encoder(AnnouncementSchema.model_validate(ann)) for ann in announcements]
        # print(f"Emitiendo announcements: {data}")
        await sio.emit("announcements", data)
    
    except Exception as e:
        print(f"Error al obtener o emitir los announcements: {e}")

    finally:
        db.close()
    


@router.get("/broadcast")
async def trigger_broadcast():
    # print("Triggering broadcast...")
    await broadcast_announcements()
    return {"message": "Broadcast realizado"}
