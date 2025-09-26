# app/routes/travels.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Travels
from app.schemas import TravelCreate, Travel, TravelUpdate

router = APIRouter(
    prefix="/travels",
    tags=["Travels"]
)

# Obtener todos los viajes con su destino y compañía de buses
@router.get("/", response_model=list[Travel])
def get_travels(db: Session = Depends(get_db)):
    travels = (
        db.query(Travels)
        .options(
            joinedload(Travels.destination),  # Carga datos del destino
            joinedload(Travels.bus_company)  # Carga datos de la compañía de buses
        )
        .all()
    )
    return travels


# Obtener un viaje por ID
@router.get("/{travel_id}")
def get_travel(travel_id: int, db: Session = Depends(get_db)):
    travel = db.query(Travels).filter(Travels.id == travel_id).first()
    if not travel:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return travel

# Crear un nuevo viaje
@router.post("/")
def create_travel(travel_data: TravelCreate, db: Session = Depends(get_db)):
    new_travel = Travels(
        id_bus_companies=travel_data.id_bus_companies,
        id_destinations=travel_data.id_destinations,
        departure_time=travel_data.departure_time,
        plate=travel_data.plate
    )
    
    db.add(new_travel)
    db.commit()
    db.refresh(new_travel)
    
    return {"message": "success", "data": new_travel}

@router.put("/{travel_id}")
def update_travel(travel_id: int, travel_data: TravelUpdate, db: Session = Depends(get_db)):
    travel = db.query(Travels).filter(Travels.id == travel_id).first()
    if not travel:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # ✅ Actualizar solo los campos enviados
    update_data = travel_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(travel, key, value)

    db.commit()
    db.refresh(travel)
    return {"message": "success", "data": travel}

# Eliminar un viaje
@router.delete("/{travel_id}")
def delete_travel(travel_id: int, db: Session = Depends(get_db)):
    travel = db.query(Travels).filter(Travels.id == travel_id).first()
    if not travel:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    db.delete(travel)
    db.commit()
    return {"message": "Viaje eliminado"}
