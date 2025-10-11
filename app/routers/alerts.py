from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app import models
from app.database import get_db

router = APIRouter(
    prefix="/api/alerts",
    tags=["alerts"]
)


@router.get("/")
def get_alerts(
    db: Session = Depends(get_db),
    resolved: Optional[bool] = Query(None, description="Filtra por alertas resueltas o no resueltas"),
    start_date: Optional[str] = Query(None, description="Fecha inicial en formato YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Fecha final en formato YYYY-MM-DD"),
    bay_id: Optional[int] = Query(None, description="Filtra por ID de bahía"),
    maintenance_id: Optional[int] = Query(None, description="Filtra por ID de mantenimiento"),
    user_id: Optional[int] = Query(None, description="Filtra por ID de usuario involucrado")
):
    """
    Devuelve todas las alertas registradas con:
    - bahía, mantenimiento, usuario, estado, fechas
    Permite filtrar por:
      • Estado (resuelto / no resuelto)
      • Rango de fechas
      • Bahía
      • Mantenimiento
      • Usuario
    """

    # Base query
    query = (
        db.query(models.Alert)
        .join(models.Maintenance, models.Maintenance.id == models.Alert.id_maintenance)
        .join(models.Bahia, models.Bahia.id == models.Maintenance.id_bahias)
        .join(models.TypeAlert, models.TypeAlert.id == models.Alert.id_types_alerts)
        .outerjoin(
            models.PeopleInMaintenance,
            models.PeopleInMaintenance.id == models.Alert.id_people_in_maintenance
        )
        .outerjoin(models.User, models.User.id == models.PeopleInMaintenance.id_users)
    )

    # ✅ Filtro por estado
    if resolved is not None:
        query = query.filter(models.Alert.resolved == resolved)

    # ✅ Filtro por fechas
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(models.Alert.alert_time >= start_dt)
        except ValueError:
            return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(models.Alert.alert_time <= end_dt)
        except ValueError:
            return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}

    # ✅ Filtro por bahía
    if bay_id:
        query = query.filter(models.Maintenance.id_bahias == bay_id)

    # ✅ Filtro por mantenimiento
    if maintenance_id:
        query = query.filter(models.Alert.id_maintenance == maintenance_id)

    # ✅ Filtro por usuario
    if user_id:
        query = query.filter(models.PeopleInMaintenance.id_users == user_id)

    # Ejecutar consulta
    alerts = query.order_by(models.Alert.alert_time.desc()).all()

    def fmt(dt):
        return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

    response = []
    for a in alerts:
        maintenance = a.maintenance
        bahia = maintenance.bahia if maintenance else None
        user = (
            a.people_in_maintenance.user
            if a.people_in_maintenance and a.people_in_maintenance.user
            else None
        )

        response.append({
            "id": a.id,
            "bayName": bahia.name if bahia else "-",
            "maintenanceName": maintenance.name if maintenance else "-",
            "type": a.type_alert.name if a.type_alert else "-",
            "status": "resuelto" if a.resolved else "no resuelto",
            "user": f"{user.name} {user.lastname}" if user else "-",
            "startTime": fmt(maintenance.start_time) if maintenance else "-",
            "endTime": fmt(maintenance.end_time) if maintenance else "-",
            "alertTime": fmt(a.alert_time),
        })

    return response


# 1️⃣ Todas las alertas:
# GET /api/alerts


# 2️⃣ Solo alertas no resueltas:
# GET /api/alerts?resolved=false


# 3️⃣ Alertas de una bahía:
# GET /api/alerts?bay_id=3


# 4️⃣ Alertas entre fechas:
# GET /api/alerts?start_date=2025-10-01&end_date=2025-10-11


# 5️⃣ Alertas de un usuario específico:
# GET /api/alerts?user_id=2


# 6️⃣ Combinado:
# GET /api/alerts?bay_id=1&resolved=false&start_date=2025-10-01