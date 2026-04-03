from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base


class AdditionalCharges(Base):
    __tablename__ = "additional_charges"

    id = Column(Integer, primary_key=True)
    name = Column(String)  # platform_fee, peak_fee
    min_value = Column(Float)
    max_value = Column(Float)
    fixed = Column(Float, nullable=True)
