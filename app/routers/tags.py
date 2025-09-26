# app/routers/tags.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)

@router.post("/", response_model=schemas.TagResponse)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == tag.id_users).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    type_tag = db.query(models.TypeTag).filter(models.TypeTag.id == tag.id_type_tag).first()
    if not type_tag:
        raise HTTPException(status_code=404, detail="Tipo de tag no encontrado")

    new_tag = models.Tag(
        tag_code=tag.tag_code,
        id_type_tag=tag.id_type_tag,
        id_users=tag.id_users
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.get("/", response_model=List[schemas.TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).all()

@router.get("/{tag_id}", response_model=schemas.TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    return tag

@router.delete("/{tag_id}", response_model=dict)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    db.delete(tag)
    db.commit()
    return {"message": "Tag eliminado correctamente"}
