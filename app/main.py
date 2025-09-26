#app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.utils.init_videos import init_video_db
from app.database import engine, Base
from app.routers import (
    announcements, 
    boarding_gates, 
    bus_companies, 
    destinations, 
    travels, 
    users, 
    socketio_announcements,
    videos, 
    socketio_videos
)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers HTTP
app.include_router(announcements.router)
app.include_router(boarding_gates.router)
app.include_router(bus_companies.router)
app.include_router(destinations.router)
app.include_router(travels.router)
app.include_router(users.router)
app.include_router(socketio_announcements.router)
app.include_router(videos.router)
app.include_router(socketio_videos.router)

# Montar la aplicación Socket.IO
app.mount("/ws/announcements", socketio_announcements.sio_app)
app.mount("/ws/videos", socketio_videos.sio_app)

# Servir archivos estáticos desde "app/public"
app.mount("/public", StaticFiles(directory="app/public"), name="public")

@app.get("/")
def root():
    return {"message": "API con Socket.IO en ejecución"}

# Crear las tablas (si no existen)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    init_video_db()