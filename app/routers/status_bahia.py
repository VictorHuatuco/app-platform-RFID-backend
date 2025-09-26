# app/routers/status_bahia.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/status_bahia",
    tags=["StatusBahia"]
)

@router.post("/", response_model=schemas.StatusBahiaResponse)
def create_status_bahia(status: schemas.StatusBahiaCreate, db: Session = Depends(get_db)):
    new_status = models.StatusBahia(name=status.name)
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return new_status

@router.get("/", response_model=List[schemas.StatusBahiaResponse])
def list_status_bahia(db: Session = Depends(get_db)):
    return db.query(models.StatusBahia).all()

@router.get("/{status_id}", response_model=schemas.StatusBahiaResponse)
def get_status_bahia(status_id: int, db: Session = Depends(get_db)):
    status = db.query(models.StatusBahia).filter(models.StatusBahia.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="StatusBahia no encontrado")
    return status

@router.delete("/{status_id}", response_model=dict)
def delete_status_bahia(status_id: int, db: Session = Depends(get_db)):
    status = db.query(models.StatusBahia).filter(models.StatusBahia.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="StatusBahia no encontrado")
    db.delete(status)
    db.commit()
    return {"message": "StatusBahia eliminado correctamente"}
