# app/routers/type_tags.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/type-tags",
    tags=["Type Tags"]
)

@router.post("/", response_model=schemas.TypeTagResponse)
def create_type_tag(type_tag: schemas.TypeTagCreate, db: Session = Depends(get_db)):

    db_type = db.query(models.TypeTag).filter(models.TypeTag.name == type_tag.name).first()
    if db_type:
        raise HTTPException(status_code=400, detail="Este tipo de tag ya existe")

    new_type_tag = models.TypeTag(name=type_tag.name)
    db.add(new_type_tag)
    db.commit()
    db.refresh(new_type_tag)
    return new_type_tag

@router.get("/", response_model=List[schemas.TypeTagResponse])
def list_type_tags(db: Session = Depends(get_db)):
    return db.query(models.TypeTag).all()

@router.get("/{type_id}", response_model=schemas.TypeTagResponse)
def get_type_tag(type_id: int, db: Session = Depends(get_db)):
    type_tag = db.query(models.TypeTag).filter(models.TypeTag.id == type_id).first()
    if not type_tag:
        raise HTTPException(status_code=404, detail="Tipo de tag no encontrado")
    return type_tag

@router.delete("/{type_id}", response_model=dict)
def delete_type_tag(type_id: int, db: Session = Depends(get_db)):
    type_tag = db.query(models.TypeTag).filter(models.TypeTag.id == type_id).first()
    if not type_tag:
        raise HTTPException(status_code=404, detail="Tipo de tag no encontrado")
    db.delete(type_tag)
    db.commit()
    return {"message": "Tipo de tag eliminado correctamente"}
