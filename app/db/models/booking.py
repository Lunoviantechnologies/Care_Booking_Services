from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from app.db.session import Base
from datetime import datetime


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

     # ✅ SERVICE INFO
    service_type = Column(String)
    duration = Column(Integer)
    persons = Column(Integer)

    # ✅ CUSTOMER DETAILS
    
    booking_date = Column(String)  # or Date
    booking_time = Column(String)

    # ✅ SERVICES
    selected_services = Column(JSON)
    extra_details = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)

    # ✅ PRICING
    base_price = Column(Float)
    extra_charges = Column(Float)
    total_amount = Column(Float)

    # ✅ FLAGS
    is_peak = Column(Boolean, default=False)
    is_emergency = Column(Boolean, default=False)
    is_subscription = Column(Boolean, default=False)

    # ✅ STATUS FLOW
    status = Column(String, default="pending")

    # ✅ WORKER
    worker_id = Column(Integer, nullable=True)

    # ✅ OTP FLOW
    start_otp = Column(String, nullable=True)
    end_otp = Column(String, nullable=True)

    # ✅ TIME TRACKING
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    working_hours = Column(Float, nullable=True)

    # ✅ RATING
    rating = Column(Float, nullable=True)

    # ✅ DISTANCE
    distance_km = Column(Float, nullable=False)

    # ✅ TIMESTAMPS
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
