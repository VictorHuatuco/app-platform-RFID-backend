# app/routes/boarding_gates.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/boarding_gates", tags=["Boarding Gates"])

@router.post("/", response_model=schemas.BoardingGate)
def create_boarding_gate(boarding_gate: schemas.BoardingGateCreate, db: Session = Depends(get_db)):
    db_boarding_gate = models.BoardingGates(**boarding_gate.dict())
    db.add(db_boarding_gate)
    db.commit()
    db.refresh(db_boarding_gate)
    return db_boarding_gate

@router.get("/", response_model=list[schemas.BoardingGate])
def list_boarding_gates(db: Session = Depends(get_db)):
    return db.query(models.BoardingGates).all()
