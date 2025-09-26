from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/destinations", tags=["Destinations"])

@router.post("/", response_model=schemas.Destination)
def create_destination(destination: schemas.DestinationCreate, db: Session = Depends(get_db)):
    db_destination = models.Destinations(**destination.dict())
    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)
    return db_destination

@router.get("/", response_model=list[schemas.Destination])
def list_destinations(db: Session = Depends(get_db)):
    return db.query(models.Destinations).all()
