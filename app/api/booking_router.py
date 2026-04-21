from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.booking_schema import BookingCreate, OTPVerify, RatingUpdate
from app.services.booking_service import (
    create_booking,
    get_dashboard_stats,
    add_rating,
    accept_booking,
    start_work,
    end_work,
    verify_end_otp,
    get_final_amount,
    list_bookings,  # ✅ NEW
    get_booking_by_id,
)

router = APIRouter(prefix="/api/booking", tags=["Booking"])


# ✅ TEMP USER (HARDCODED)
DUMMY_USER_ID = 1
DUMMY_WORKER_ID = 1


# ================= CREATE =================
@router.post("/create")
async def create(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await create_booking(data, DUMMY_USER_ID, db)

    if not result:
        raise HTTPException(404, "Pricing not found")

    booking, extra = result

    return {
        "booking_id": booking.id,
        "total_amount": booking.total_amount,
        "status": booking.status,
        "start_otp": booking.start_otp,
    }


# ================= DASHBOARD =================
@router.get("/dashboard")
async def dashboard(
    user_id: int = Header(..., alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
):
    return await get_dashboard_stats(user_id, db)


# ================= ADD RATING =================
@router.post("/rate/{booking_id}")
async def rate(
    booking_id: int,
    data: RatingUpdate,
    db: AsyncSession = Depends(get_db),
):
    booking = await add_rating(booking_id, data.rating, db)

    if not booking:
        raise HTTPException(404, "Booking not found")

    return {"message": "Rating added"}


# ================= ACCEPT =================
@router.post("/accept/{booking_id}")
async def accept(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    booking, msg = await accept_booking(booking_id, DUMMY_WORKER_ID, db)

    if not booking:
        raise HTTPException(404, msg)

    return {"message": msg}


# ================= START (OTP VERIFY) =================
@router.post("/start/{booking_id}")
async def start(
    booking_id: int,
    data: OTPVerify,
    db: AsyncSession = Depends(get_db),
):
    booking, msg = await start_work(booking_id, data.otp, db)

    if not booking:
        raise HTTPException(400, msg)

    return {"message": msg, "status": booking.status}


# ================= END =================
@router.post("/end/{booking_id}")
async def end(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    booking, msg = await end_work(booking_id, db)

    if not booking:
        raise HTTPException(404, msg)

    return {"message": msg, "end_otp": booking.end_otp}


# ================= VERIFY END OTP =================
@router.post("/verify/{booking_id}")
async def verify(
    booking_id: int,
    data: OTPVerify,
    db: AsyncSession = Depends(get_db),
):
    booking, msg = await verify_end_otp(booking_id, data.otp, db)

    if not booking:
        raise HTTPException(400, msg)

    return {"message": msg, "final_amount": booking.total_amount}


# ================= FINAL AMOUNT =================
@router.get("/final-amount/{booking_id}")
async def final_amount(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await get_final_amount(booking_id, db)

    if not result:
        raise HTTPException(404, "Booking not found")

    return result


#getAll bookings
@router.get("/all")
async def get_all(
    page: int = 1,
    size: int = 10,
    service_type: str = None,
    selected_service: str = None,
    db: AsyncSession = Depends(get_db),
):
    return await list_bookings(db, page, size, service_type, selected_service)


# getbyid booking
@router.get("/{booking_id}")
async def get_by_id(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    booking = await get_booking_by_id(booking_id, db)

    if not booking:
        raise HTTPException(404, "Booking not found")

    return booking
