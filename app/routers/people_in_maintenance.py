# app/routers/people_in_maintenance.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/people_in_maintenance",
    tags=["people_in_maintenance"]
)

# Crear registro de persona en mantenimiento
@router.post("/", response_model=schemas.PeopleInMaintenanceResponse)
def create_person_in_maintenance(data: schemas.PeopleInMaintenanceCreate, db: Session = Depends(get_db)):
    db_record = models.PeopleInMaintenance(**data.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# Listar personas en mantenimientos
@router.get("/", response_model=List[schemas.PeopleInMaintenanceResponse])
def get_people_in_maintenance_list(db: Session = Depends(get_db)):
    return db.query(models.PeopleInMaintenance).all()

# Obtener por ID
@router.get("/{record_id}", response_model=schemas.PeopleInMaintenanceResponse)
def get_person_in_maintenance(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.PeopleInMaintenance).filter(models.PeopleInMaintenance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record

# Actualizar registro
@router.put("/{record_id}", response_model=schemas.PeopleInMaintenanceResponse)
def update_person_in_maintenance(record_id: int, updated: schemas.PeopleInMaintenanceCreate, db: Session = Depends(get_db)):
    record = db.query(models.PeopleInMaintenance).filter(models.PeopleInMaintenance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    for key, value in updated.dict().items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

# Eliminar registro
@router.delete("/{record_id}")
def delete_person_in_maintenance(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.PeopleInMaintenance).filter(models.PeopleInMaintenance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    db.delete(record)
    db.commit()
    return {"message": "Registro eliminado exitosamente"}
