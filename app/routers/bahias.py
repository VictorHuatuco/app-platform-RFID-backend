# app/api/bahias.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/bahias", tags=["Bahías"])


@router.get("/")
def get_bahias(db: Session = Depends(get_db)):
    """
    Retorna la lista de bahías con su estado actual:
    - available: online sin alertas ni mantenimiento activo
    - inManteinance: mantenimiento activo
    - alert: alerta activa en el mantenimiento actual o último
    - moduleDisconnected: módulo offline
    """
    bahias = db.query(models.Bahia).all()

    response = []
    for b in bahias:
        # Buscar mantenimiento actual o el más reciente
        maintenance = (
            db.query(models.Maintenance)
            .filter(models.Maintenance.id_bahias == b.id)
            .order_by(models.Maintenance.start_time.desc())
            .first()
        )

        # Buscar alertas no resueltas asociadas al mantenimiento actual o último
        active_alerts = 0
        if maintenance:
            active_alerts = (
                db.query(models.Alert)
                .filter(models.Alert.id_maintenance == maintenance.id)
                .filter(models.Alert.resolved == False)
                .count()
            )

        # --- Determinar status lógico ---
        if b.module_loto_status == "offline":
            status_name = "moduleDisconnected"
        elif maintenance and maintenance.end_time is None:
            status_name = "inManteinance"
        elif active_alerts > 0:
            status_name = "alert"
        else:
            status_name = "available"

        # --- Formatear tiempos ---
        def fmt(dt):
            return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

        start_time = fmt(maintenance.start_time) if maintenance else "-"
        end_time = fmt(maintenance.end_time) if maintenance else "-"

        # --- Icono ---
        icon = "warning" if status_name in ["alert", "inManteinance"] else "check"

        response.append({
            "id": b.id,
            "name": b.name,
            "status": status_name,
            "code": b.module_loto_code,
            "start_time": start_time,
            "end_time": end_time,
            "icon": icon
        })

    return response


@router.get("/{bahia_id}/maintenance")
def get_bahia_maintenance_details(bahia_id: int, db: Session = Depends(get_db)):
    """
    Devuelve la información del mantenimiento más reciente o activo de una bahía específica.
    Incluye los usuarios involucrados, sus tiempos de entrada/salida y si hubo alertas.
    """
    # 1️⃣ Buscar la bahía
    bahia = db.query(models.Bahia).filter(models.Bahia.id == bahia_id).first()
    if not bahia:
        raise HTTPException(status_code=404, detail="Bahía no encontrada")

    # 2️⃣ Buscar mantenimiento activo o más reciente
    maintenance = (
        db.query(models.Maintenance)
        .filter(models.Maintenance.id_bahias == bahia_id)
        .order_by(models.Maintenance.start_time.desc())
        .first()
    )

    if not maintenance:
        raise HTTPException(status_code=404, detail="No hay mantenimientos registrados para esta bahía")

    # 3️⃣ Obtener personas en mantenimiento
    people = (
        db.query(models.PeopleInMaintenance)
        .join(models.User, models.User.id == models.PeopleInMaintenance.id_users)
        .filter(models.PeopleInMaintenance.id_maintenance == maintenance.id)
        .all()
    )

    # 4️⃣ Verificar alertas en ese mantenimiento
    alerts_exist = (
        db.query(models.Alert)
        .filter(models.Alert.id_maintenance == maintenance.id)
        .count() > 0
    )

    # 5️⃣ Helper para formatear fechas
    def fmt(dt):
        return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

    # 6️⃣ Construir respuesta
    users_details = [
        {
            "name": p.user.name,
            "lastName": p.user.lastname,
            "email": p.user.email,
            "initTime": fmt(p.entry_time),
            "endTime": fmt(p.exit_time),
        }
        for p in people
    ]

    response = {
        "id": maintenance.id,
        "bayName": bahia.name,
        "maintenanceName": maintenance.name or "-",
        "cantUsers": len(users_details),
        "usersDetails": users_details,
        "startTime": fmt(maintenance.start_time),
        "endTime": fmt(maintenance.end_time),
        "alerts": "Sí" if alerts_exist else "No",
    }

    return response



# 1️⃣ Todas las alertas:
# GET /api/bahias


# 2️⃣ Solo alertas no resueltas:
# GET /api/bahias/1/maintenance

