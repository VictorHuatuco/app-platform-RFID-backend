# app/routers/alerts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"]
)

# Crear alerta
@router.post("/", response_model=schemas.AlertResponse)
def create_alert(data: schemas.AlertCreate, db: Session = Depends(get_db)):
    db_alert = models.Alert(**data.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

# Listar alertas
@router.get("/", response_model=List[schemas.AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).all()

# Obtener alerta por ID
@router.get("/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alert

# Actualizar alerta
@router.put("/{alert_id}", response_model=schemas.AlertResponse)
def update_alert(alert_id: int, updated: schemas.AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    data = updated.dict(exclude_unset=True)

    # Si se resolvió y no viene fecha, la ponemos automáticamente
    if data.get("resolved") and not data.get("resolved_at"):
        data["resolved_at"] = datetime.now()

    for key, value in data.items():
        setattr(alert, key, value)

    db.commit()
    db.refresh(alert)
    return alert



# Eliminar alerta
@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alerta eliminada exitosamente"}
