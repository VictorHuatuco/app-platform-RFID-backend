# app/routers/bahia.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/bahias",
    tags=["Bahias"]
)

@router.post("/", response_model=schemas.BahiaResponse)
def create_bahia(bahia: schemas.BahiaCreate, db: Session = Depends(get_db)):
    sede = db.query(models.Sede).filter(models.Sede.id == bahia.sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    status = db.query(models.StatusBahia).filter(models.StatusBahia.id == bahia.status_bahia_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="StatusBahia no encontrado")

    new_bahia = models.Bahia(
        name=bahia.name,
        sede_id=bahia.sede_id,
        status_bahia_id=bahia.status_bahia_id,
        module_loto_code=bahia.module_loto_code,
        module_loto_status=bahia.module_loto_status or "offline"
    )
    db.add(new_bahia)
    db.commit()
    db.refresh(new_bahia)
    return new_bahia

@router.get("/", response_model=List[schemas.BahiaResponse])
def list_bahias(db: Session = Depends(get_db)):
    return db.query(models.Bahia).all()

@router.get("/{bahia_id}", response_model=schemas.BahiaResponse)
def get_bahia(bahia_id: int, db: Session = Depends(get_db)):
    bahia = db.query(models.Bahia).filter(models.Bahia.id == bahia_id).first()
    if not bahia:
        raise HTTPException(status_code=404, detail="Bahia no encontrada")
    return bahia

@router.put("/{bahia_id}", response_model=schemas.BahiaResponse)
def update_bahia(bahia_id: int, bahia_data: schemas.BahiaCreate, db: Session = Depends(get_db)):
    bahia = db.query(models.Bahia).filter(models.Bahia.id == bahia_id).first()
    if not bahia:
        raise HTTPException(status_code=404, detail="Bahia no encontrada")

    bahia.name = bahia_data.name
    bahia.sede_id = bahia_data.sede_id
    bahia.status_bahia_id = bahia_data.status_bahia_id
    bahia.module_loto_code = bahia_data.module_loto_code
    bahia.module_loto_status = bahia_data.module_loto_status or bahia.module_loto_status

    db.commit()
    db.refresh(bahia)
    return bahia

@router.delete("/{bahia_id}", response_model=dict)
def delete_bahia(bahia_id: int, db: Session = Depends(get_db)):
    bahia = db.query(models.Bahia).filter(models.Bahia.id == bahia_id).first()
    if not bahia:
        raise HTTPException(status_code=404, detail="Bahia no encontrada")

    db.delete(bahia)
    db.commit()
    return {"message": "Bahia eliminada correctamente"}
