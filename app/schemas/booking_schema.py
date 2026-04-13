from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# ================= CREATE =================
class BookingCreate(BaseModel):
    service_type: str
    duration: int
    persons: int

    # full_name: str
    booking_date: str
    booking_time: str

    selected_services: List[str]
    extra_details: Dict
    notes: Optional[str] = None

    is_peak: bool = False
    is_emergency: bool = False
    is_subscription: bool = False

    distance_km: float


# ================= OTP =================
class OTPVerify(BaseModel):
    otp: str


# ================= RATING (FIXED ERROR) =================
class RatingUpdate(BaseModel):
    rating: float


# ================= RESPONSE =================
class BookingResponse(BaseModel):
    id: int
    customer_id: int

    service_type: str
    duration: int
    persons: int

    full_name: Optional[str]
    booking_date: Optional[str]
    booking_time: Optional[str]

    total_amount: float
    status: str

    rating: Optional[float] = None
    working_hours: Optional[float] = None

    created_at: Optional[datetime]

    class Config:
        from_attributes = True
