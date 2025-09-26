from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/bus_companies", tags=["Bus Companies"])

@router.post("/", response_model=schemas.BusCompany)
def create_bus_company(bus_company: schemas.BusCompanyCreate, db: Session = Depends(get_db)):
    db_bus_company = models.BusCompanies(**bus_company.dict())
    db.add(db_bus_company)
    db.commit()
    db.refresh(db_bus_company)
    return db_bus_company

@router.get("/", response_model=list[schemas.BusCompany])
def list_bus_companies(db: Session = Depends(get_db)):
    return db.query(models.BusCompanies).all()
