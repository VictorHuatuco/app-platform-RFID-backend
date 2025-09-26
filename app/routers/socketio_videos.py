#app/socketio_videos.py
import socketio
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Videos
from app.schemas import Video as VideoSchema
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import asyncio

# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
# sio_app = socketio.ASGIApp(sio)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="http://localhost:4200")
# sio_app = socketio.ASGIApp(sio, socketio_path="/socket.io")
sio_app = socketio.ASGIApp(sio, socketio_path="/ws/videos/socket.io")

router = APIRouter()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@sio.event
async def connect(sid, environ):
    print(f"Socket.IO (videos): Cliente conectado: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Socket.IO (videos): Cliente desconectado: {sid}")

async def broadcast_videos():
    db = SessionLocal()
    try:
        print("Obteniendo videos de la base de datos...")
        videos = db.query(Videos).order_by(Videos.order).all()

        if not videos:
            print("No se encontraron videos en la base de datos.")
        else:
            print(f"Videos obtenidos: {videos}")

        data = [jsonable_encoder(VideoSchema.model_validate(video)) for video in videos]
                # Emitir los datos a los clientes conectados
        print(f"Emitiendo videos: {data}")  # Esto es útil para depuración
        await sio.emit("videos", data)

    except Exception as e:
        print(f"Error al obtener o emitir los videos: {e}")
    finally:
        db.close()

@router.get("/broadcast")
async def trigger_video_broadcast():
    print("Triggering broadcast...")
    await broadcast_videos()
    return {"message": "Broadcast videos realizado"}
