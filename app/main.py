# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.create_db import reset_database
from app.routers import (
    users,
    type_tags,
    tags,
    headquarters,
    status_bahia,
    bahia,
    maintenance,
    people_in_maintenance,
    type_alerts,
    alerts,
)

# ⬇️ MQTT
from app.mqtt.client import MqttService

app = FastAPI(
    title="IoT Platform API",
    description="Backend para la plataforma IoT con FastAPI y PostgreSQL",
    version="1.0.0",
)

# Configuración CORS (ajusta dominios en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers HTTP
app.include_router(users.router)
app.include_router(type_tags.router)
app.include_router(tags.router)
app.include_router(headquarters.router)
app.include_router(status_bahia.router)
app.include_router(bahia.router)
app.include_router(maintenance.router)
app.include_router(people_in_maintenance.router)
app.include_router(type_alerts.router)
app.include_router(alerts.router)


# Si quieres servir archivos estáticos (ej: imágenes, documentos, calibraciones)
app.mount("/public", StaticFiles(directory="app/public"), name="public")

# MQTT service instance
mqtt_service = MqttService()

# Evento al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    reset_database()
    print("✅ Base de datos lista y tablas creadas/verificadas.")

    # Iniciar MQTT
    mqtt_service.start()
    print("🔗 MQTT loop iniciado")

@app.get("/")
def root():
    return {"message": "🚀 API IoT en ejecución"}

@app.on_event("shutdown")
def shutdown_event():
    mqtt_service.stop()
    print("🛑 MQTT loop detenido")