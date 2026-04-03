# pricing_model.py

from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base


class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, index=True)

    service_type = Column(String)     # baby_care, pregnancy_care...
    duration = Column(Integer)        # hours (1,2,4,8)
    price = Column(Float)

    # optional conditions
    min_persons = Column(Integer, nullable=True)
    max_persons = Column(Integer, nullable=True)