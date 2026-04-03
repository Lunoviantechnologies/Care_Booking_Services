from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.session import Base
from datetime import datetime


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    service_type = Column(String)
    duration = Column(Integer)
    persons = Column(Integer)

    base_price = Column(Float)
    extra_charges = Column(Float)
    total_amount = Column(Float)

    status = Column(String, default="pending")

    worker_id = Column(Integer, nullable=True)

    start_otp = Column(String, nullable=True)
    end_otp = Column(String, nullable=True)

    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    working_hours = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ FIXED (NO MIXED STYLE)
    distance_km = Column(Float, nullable=False)
