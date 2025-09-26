# app/routers/type_alerts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/type_alerts",
    tags=["type_alerts"]
)

# Crear tipo de alerta
@router.post("/", response_model=schemas.TypeAlertResponse)
def create_type_alert(data: schemas.TypeAlertCreate, db: Session = Depends(get_db)):
    db_type_alert = models.TypeAlert(**data.dict())
    db.add(db_type_alert)
    db.commit()
    db.refresh(db_type_alert)
    return db_type_alert

# Listar tipos de alerta
@router.get("/", response_model=List[schemas.TypeAlertResponse])
def get_type_alerts(db: Session = Depends(get_db)):
    return db.query(models.TypeAlert).all()

# Obtener tipo de alerta por ID
@router.get("/{type_alert_id}", response_model=schemas.TypeAlertResponse)
def get_type_alert(type_alert_id: int, db: Session = Depends(get_db)):
    type_alert = db.query(models.TypeAlert).filter(models.TypeAlert.id == type_alert_id).first()
    if not type_alert:
        raise HTTPException(status_code=404, detail="Tipo de alerta no encontrado")
    return type_alert

# Actualizar tipo de alerta
@router.put("/{type_alert_id}", response_model=schemas.TypeAlertResponse)
def update_type_alert(type_alert_id: int, updated: schemas.TypeAlertCreate, db: Session = Depends(get_db)):
    type_alert = db.query(models.TypeAlert).filter(models.TypeAlert.id == type_alert_id).first()
    if not type_alert:
        raise HTTPException(status_code=404, detail="Tipo de alerta no encontrado")
    
    for key, value in updated.dict().items():
        setattr(type_alert, key, value)

    db.commit()
    db.refresh(type_alert)
    return type_alert

# Eliminar tipo de alerta
@router.delete("/{type_alert_id}")
def delete_type_alert(type_alert_id: int, db: Session = Depends(get_db)):
    type_alert = db.query(models.TypeAlert).filter(models.TypeAlert.id == type_alert_id).first()
    if not type_alert:
        raise HTTPException(status_code=404, detail="Tipo de alerta no encontrado")
    
    db.delete(type_alert)
    db.commit()
    return {"message": "Tipo de alerta eliminado exitosamente"}
