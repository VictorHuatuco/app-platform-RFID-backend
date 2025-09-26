# app/routers/headquarters.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/headquarters",
    tags=["Headquarters"]
)

@router.post("/", response_model=schemas.HeadquartersResponse)
def create_headquarters(headquarters: schemas.HeadquartersCreate, db: Session = Depends(get_db)):
    new_headquarters = models.Headquarters(name=headquarters.name)
    db.add(new_headquarters)
    db.commit()
    db.refresh(new_headquarters)
    return new_headquarters

@router.get("/", response_model=List[schemas.HeadquartersResponse])
def list_headquarters(db: Session = Depends(get_db)):
    return db.query(models.Headquarters).all()

@router.get("/{hq_id}", response_model=schemas.HeadquartersResponse)
def get_headquarters(hq_id: int, db: Session = Depends(get_db)):
    hq = db.query(models.Headquarters).filter(models.Headquarters.id == hq_id).first()
    if not hq:
        raise HTTPException(status_code=404, detail="Headquarters no encontrado")
    return hq

@router.delete("/{hq_id}", response_model=dict)
def delete_headquarters(hq_id: int, db: Session = Depends(get_db)):
    hq = db.query(models.Headquarters).filter(models.Headquarters.id == hq_id).first()
    if not hq:
        raise HTTPException(status_code=404, detail="Headquarters no encontrado")
    db.delete(hq)
    db.commit()
    return {"message": "Headquarters eliminado correctamente"}
