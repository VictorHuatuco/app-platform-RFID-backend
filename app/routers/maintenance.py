# app/routers/maintenance.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models
from app.database import get_db
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/")
def get_mantenimientos(
    db: Session = Depends(get_db),
    bay_id: Optional[int] = Query(None, description="Filtra por ID de bahía"),
    start_date: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
):
    """
    Devuelve el historial de mantenimientos con posibilidad de filtrar por:
    - Bahía (`bay_id`)
    - Rango de fechas (`start_date`, `end_date`)
    Si no se encuentran resultados, devuelve un mensaje adecuado.
    """
    query = (
        db.query(models.Maintenance)
        .join(models.Bahia, models.Bahia.id == models.Maintenance.id_bahias)
        .order_by(models.Maintenance.start_time.desc())
    )

    # ✅ Validar existencia de la bahía antes de filtrar
    if bay_id:
        bahia_exists = db.query(models.Bahia).filter(models.Bahia.id == bay_id).first()
        if not bahia_exists:
            return {
                "message": f"No existe una bahía con ID {bay_id}.",
                "data": []
            }
        query = query.filter(models.Maintenance.id_bahias == bay_id)

    # ✅ Filtro por rango de fechas
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(models.Maintenance.start_time >= start_dt)
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(models.Maintenance.start_time <= end_dt)
    except ValueError:
        return {"message": "Formato de fecha inválido. Usa YYYY-MM-DD", "data": []}


    maintenances = query.all()

    # ✅ Si no se encontraron mantenimientos
    if not maintenances:
        msg = "No se encontraron mantenimientos registrados."
        if bay_id:
            msg = f"No hay mantenimientos registrados para la bahía con ID {bay_id}."
        if start_date or end_date:
            msg += " No hay registros dentro del rango de fechas indicado."
        return {"message": "empty", "data": []}

    # Helper para formato de hora
    def fmt(dt):
        return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

    response_data = []
    for m in maintenances:
        user_count = (
            db.query(models.PeopleInMaintenance)
            .filter(models.PeopleInMaintenance.id_maintenance == m.id)
            .count()
        )

        alerts_exist = (
            db.query(models.Alert)
            .filter(models.Alert.id_maintenance == m.id)
            .count()
        ) > 0

        response_data.append({
            "id": m.id,
            "bayName": m.bahia.name if m.bahia else "-",
            "maintenanceName": m.name or "-",
            "users": user_count,
            "startTime": fmt(m.start_time),
            "endTime": fmt(m.end_time),
            "status": m.status,
            "alerts": "sí" if alerts_exist else "no",
        })

    return {
        "message": "success",
        "data": response_data
    }


@router.get("/{maintenance_id}")
def get_mantenimiento_detalle(maintenance_id: int, db: Session = Depends(get_db)):
    """
    Devuelve los detalles de un mantenimiento específico:
    - id, bayName, maintenanceName
    - número total de usuarios
    - lista de usuarios con su entry_time y exit_time
    - startTime, endTime, alertas
    Devuelve {"message": "empty"} si no hay usuarios vinculados o el mantenimiento no existe.
    """
    # 🔍 Buscar mantenimiento
    m = (
        db.query(models.Maintenance)
        .filter(models.Maintenance.id == maintenance_id)
        .join(models.Bahia, models.Bahia.id == models.Maintenance.id_bahias)
        .first()
    )

    if not m:
        return {"message": "not_found", "data": None}

    # 🕒 Formato de fechas
    def fmt(dt):
        return dt.strftime("%H:%M:%S %d-%m-%Y") if dt else "-"

    # 👥 Buscar usuarios del mantenimiento
    people_records = (
        db.query(models.PeopleInMaintenance, models.User)
        .join(models.User, models.User.id == models.PeopleInMaintenance.id_users)
        .filter(models.PeopleInMaintenance.id_maintenance == m.id)
        .all()
    )

    if not people_records:
        return {"message": "empty", "data": None}

    # 📋 Detalle de usuarios
    users_details = [
        {
            "name": user.name,
            "lastName": user.lastname,
            "email": user.email,
            "initTime": fmt(pim.entry_time),
            "endTime": fmt(pim.exit_time),
        }
        for pim, user in people_records
    ]

    # 🚨 Verificar si hay alertas activas o históricas
    alerts_exist = (
        db.query(models.Alert)
        .filter(models.Alert.id_maintenance == m.id)
        .count()
    ) > 0

    # 🧩 Construcción de la respuesta
    data = {
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

    return {"message": "success", "data": data}



# 1️⃣ Todos los mantenimientos:
# GET /api/maintenance

# 2️⃣ Mantenimientos de una bahía:
# GET /api/maintenance?bay_id=1

# 3️⃣ Mantenimientos entre fechas:
# GET /api/maintenance?start_date=2025-10-01&end_date=2025-10-11

# 4️⃣ Combinado (bahía y fechas):
# GET /api/maintenance?bay_id=1&start_date=2025-10-01&end_date=2025-10-11
# GET /api/maintenance?bay_id=1&start_date=2025-10-01
# GET /api/maintenance?bay_id=1&end_date=2025-10-01