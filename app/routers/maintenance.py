from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/")
def get_mantenimientos(
    db: Session = Depends(get_db),
    bay_id: Optional[int] = Query(None, description="Filtra por ID de bahía"),
    start_date: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filtra por estado del mantenimiento (active o finished)")
):
    """
    Devuelve el historial de mantenimientos con posibilidad de filtrar por:
    - Bahía (`bay_id`)
    - Rango de fechas (`start_date`, `end_date`)
    - Estado (`status` = active o finished)
    """
    query = (
        db.query(models.Maintenance)
        .join(models.Bahia, models.Bahia.id == models.Maintenance.id_bahias)
        .order_by(models.Maintenance.start_time.desc())
    )

    # ✅ Filtro por bahía
    if bay_id:
        query = query.filter(models.Maintenance.id_bahias == bay_id)

    # ✅ Filtro por fechas
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(models.Maintenance.start_time >= start_dt)
        except ValueError:
            return {"error": "Formato de start_date inválido. Usa YYYY-MM-DD"}

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(models.Maintenance.start_time <= end_dt)
        except ValueError:
            return {"error": "Formato de end_date inválido. Usa YYYY-MM-DD"}

    # ✅ Filtro por estado
    if status:
        if status not in ["active", "finished"]:
            return {"error": "El estado debe ser 'active' o 'finished'"}
        query = query.filter(models.Maintenance.status == status)

    maintenances = query.all()

    # Helper para formato de hora
    def fmt(dt):
        return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

    response = []
    for m in maintenances:
        # Contar usuarios vinculados
        user_count = (
            db.query(models.PeopleInMaintenance)
            .filter(models.PeopleInMaintenance.id_maintenance == m.id)
            .count()
        )

        # Verificar si tuvo alertas
        alerts_exist = (
            db.query(models.Alert)
            .filter(models.Alert.id_maintenance == m.id)
            .count()
        ) > 0

        response.append({
            "id": m.id,
            "bayName": m.bahia.name if m.bahia else "-",
            "maintenanceName": m.name or "-",
            "users": user_count,
            "startTime": fmt(m.start_time),
            "endTime": fmt(m.end_time),
            "status": m.status,
            "alerts": "sí" if alerts_exist else "no",
        })

    return response


@router.get("/{maintenance_id}")
def get_mantenimiento_detalle(maintenance_id: int, db: Session = Depends(get_db)):
    """
    Devuelve los detalles de un mantenimiento específico:
    - id, bayName, maintenanceName
    - número total de usuarios
    - lista de usuarios con su entry_time y exit_time
    - startTime, endTime, alertas
    """
    # Buscar mantenimiento
    m = (
        db.query(models.Maintenance)
        .filter(models.Maintenance.id == maintenance_id)
        .join(models.Bahia, models.Bahia.id == models.Maintenance.id_bahias)
        .first()
    )
    if not m:
        return {"error": "Mantenimiento no encontrado"}

    # Formateo de fecha
    def fmt(dt):
        return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

    # Buscar usuarios asociados al mantenimiento
    people_records = (
        db.query(models.PeopleInMaintenance, models.User)
        .join(models.User, models.User.id == models.PeopleInMaintenance.id_users)
        .filter(models.PeopleInMaintenance.id_maintenance == m.id)
        .all()
    )

    users_details = []
    for pim, user in people_records:
        users_details.append({
            "name": user.name,
            "lastName": user.lastname,
            "email": user.email,
            "initTime": fmt(pim.entry_time),
            "endTime": fmt(pim.exit_time),
        })

    # Verificar si hay alertas activas o históricas
    alerts_exist = (
        db.query(models.Alert)
        .filter(models.Alert.id_maintenance == m.id)
        .count()
    ) > 0

    return {
        "id": m.id,
        "bayName": m.bahia.name if m.bahia else "-",
        "maintenanceName": m.name or "-",
        "cantUsers": len(users_details),
        "usersDetails": users_details,
        "startTime": fmt(m.start_time),
        "endTime": fmt(m.end_time),
        "status": m.status,
        "alerts": "Sí" if alerts_exist else "No",
    }

# 1️⃣ Todos los mantenimientos:
# GET /api/maintenance

# 2️⃣ Mantenimientos de una bahía:
# GET /api/maintenance?bay_id=1

# 3️⃣ Mantenimientos entre fechas:
# GET /api/maintenance?start_date=2025-10-01&end_date=2025-10-11

# 4️⃣ Solo activos:
# GET /api/maintenance?status=active

# 5️⃣ Combinado (bahía 1 y activos):
# GET /api/maintenance?bay_id=1&status=active