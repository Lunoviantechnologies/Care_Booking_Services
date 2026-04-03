from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.booking_schema import BookingCreate, OTPVerify
from app.services.booking_service import *

router = APIRouter(prefix="/api/booking", tags=["Booking"])


# ================= CREATE =================
@router.post("/create")
async def create(data: BookingCreate, db: AsyncSession = Depends(get_db)):
    result = await create_booking(data, db)

    if not result:
        raise HTTPException(status_code=404, detail="Pricing not found")

    booking, extra_data = result

    return {
        "booking_id": booking.id,
        "price_breakdown": {
            "base_price": booking.base_price,
            "base_extra": extra_data["base_extra"],
            "convenience_fee": extra_data["convenience_fee"],
            "transport_fee": extra_data["transport_fee"],
            "peak_charge": extra_data["peak_charge"],
            "emergency_charge": extra_data["emergency_charge"],
            "total_extra": extra_data["total_extra"],
        },
        "total_amount": booking.total_amount,
        "start_otp": booking.start_otp,
        "status": booking.status,
    }


# ================= AVAILABLE =================
@router.get("/available")
async def available(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await get_available_bookings(worker_id, db)


# ================= ACCEPT =================
@router.post("/accept/{booking_id}")
async def accept(booking_id: int, worker_id: int, db: AsyncSession = Depends(get_db)):
    booking, msg = await accept_booking(booking_id, worker_id, db)

    if not booking:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": msg}


# ================= START =================
@router.post("/start/{booking_id}")
async def start(booking_id: int, data: OTPVerify, db: AsyncSession = Depends(get_db)):
    booking, msg = await start_work(booking_id, data.otp, db)

    if not booking:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": msg}


# ================= END =================
@router.post("/end/{booking_id}")
async def end(booking_id: int, db: AsyncSession = Depends(get_db)):
    booking, msg = await end_work(booking_id, db)

    if not booking:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": msg, "end_otp": booking.end_otp}


# ================= VERIFY =================
@router.post("/verify/{booking_id}")
async def verify(booking_id: int, data: OTPVerify, db: AsyncSession = Depends(get_db)):
    booking, msg = await verify_end_otp(booking_id, data.otp, db)

    if not booking:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": msg, "final_amount": booking.total_amount}


# ================= FINAL AMOUNT =================
@router.get("/final-amount/{booking_id}")
async def get_amount(booking_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_final_amount(booking_id, db)

    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")

    return result
