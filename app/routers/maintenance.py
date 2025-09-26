# app/routers/maintenance.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/maintenance",
    tags=["maintenance"]
)

# Crear mantenimiento
@router.post("/", response_model=schemas.MaintenanceResponse)
def create_maintenance(maintenance: schemas.MaintenanceCreate, db: Session = Depends(get_db)):
    db_maintenance = models.Maintenance(**maintenance.dict())
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

# Listar mantenimientos
@router.get("/", response_model=List[schemas.MaintenanceResponse])
def get_maintenance_list(db: Session = Depends(get_db)):
    return db.query(models.Maintenance).all()

# Obtener mantenimiento por ID
@router.get("/{maintenance_id}", response_model=schemas.MaintenanceResponse)
def get_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance = db.query(models.Maintenance).filter(models.Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    return maintenance

# Actualizar mantenimiento
@router.put("/{maintenance_id}", response_model=schemas.MaintenanceResponse)
def update_maintenance(maintenance_id: int, updated: schemas.MaintenanceCreate, db: Session = Depends(get_db)):
    maintenance = db.query(models.Maintenance).filter(models.Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    
    for key, value in updated.dict().items():
        setattr(maintenance, key, value)

    db.commit()
    db.refresh(maintenance)
    return maintenance

# Eliminar mantenimiento
@router.delete("/{maintenance_id}")
def delete_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance = db.query(models.Maintenance).filter(models.Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    
    db.delete(maintenance)
    db.commit()
    return {"message": "Mantenimiento eliminado exitosamente"}
