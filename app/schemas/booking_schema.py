from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BookingCreate(BaseModel):
    service_type: str
    duration: int
    persons: int

    is_peak: bool = False
    is_emergency: bool = False
    is_subscription: bool = False

    # ✅ REQUIRED
    distance_km: float


class OTPVerify(BaseModel):
    otp: str


class BookingResponse(BaseModel):
    id: int
    service_type: str
    duration: int
    persons: int
    total_amount: float
    status: str

    class Config:
        from_attributes = True
