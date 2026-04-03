# pricing_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.pricing_schema import PricingCreate
from app.services.pricing_service import *

router = APIRouter(prefix="/api/pricing")


# pricing_router.py

@router.get("/all")
def get_all(db: Session = Depends(get_db)):
    return db.query(Pricing).all()


@router.post("/create")
def create(data: PricingCreate, db: Session = Depends(get_db)):
    pricing = Pricing(**data.dict())
    db.add(pricing)
    db.commit()
    return pricing


@router.put("/update/{id}")
def update(id: int, data: PricingCreate, db: Session = Depends(get_db)):
    pricing = db.query(Pricing).filter(Pricing.id == id).first()

    if not pricing:
        return {"message": "Not found"}

    for key, value in data.dict().items():
        setattr(pricing, key, value)

    db.commit()
    return pricing


@router.delete("/delete/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    pricing = db.query(Pricing).filter(Pricing.id == id).first()

    if not pricing:
        return {"message": "Not found"}

    db.delete(pricing)
    db.commit()

    return {"message": "Deleted"}