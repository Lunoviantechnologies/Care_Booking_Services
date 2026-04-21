import random
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.booking import Booking
from app.db.models.pricing import Pricing


# ================= OTP =================
def generate_otp():
    return str(random.randint(1000, 9999))


# ================= PRICE =================
async def get_price(service_type, duration, persons, db):
    result = await db.execute(
        select(Pricing).where(
            Pricing.service_type == service_type, Pricing.duration == duration
        )
    )

    pricing = result.scalars().first()
    return pricing.price if pricing else None


# ================= EXTRA =================
def calculate_extra(data):
    base = 49
    convenience = 0 if data.is_subscription else 29
    transport = 0 if data.distance_km <= 5 else 29 if data.distance_km <= 10 else 49
    peak = 50 if data.is_peak else 0
    emergency = 100 if data.is_emergency else 0

    total = base + convenience + transport + peak + emergency

    return {
        "base_extra": base,
        "convenience_fee": convenience,
        "transport_fee": transport,
        "peak_charge": peak,
        "emergency_charge": emergency,
        "total_extra": total,
    }


# ================= CREATE =================
async def create_booking(data, user_id, db):

    price = await get_price(data.service_type, data.duration, data.persons, db)

    if not price:
        return None

    extra = calculate_extra(data)
    total = price + extra["total_extra"]

    booking = Booking(
        # customer_id=user_id,
        service_type=data.service_type,
        duration=data.duration,
        persons=data.persons,
        #  full_name=data.full_name,
        booking_date=data.booking_date,
        booking_time=data.booking_time,
        selected_services=data.selected_services,
        extra_details=data.extra_details,
        notes=data.notes,
        base_price=price,
        extra_charges=extra["total_extra"],
        total_amount=total,
        status="pending",
        start_otp=generate_otp(),  # ✅ OTP GENERATED HERE
        distance_km=data.distance_km,
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    return booking, extra


# ================= DASHBOARD =================
async def get_dashboard_stats(user_id, db):

    active = await db.execute(
        select(func.count()).where(
            Booking.customer_id == user_id,
            Booking.status.in_(["pending", "accepted", "started"]),
        )
    )

    past = await db.execute(
        select(func.count()).where(
            Booking.customer_id == user_id,
            Booking.status == "completed",
        )
    )

    rating = await db.execute(
        select(func.avg(Booking.rating)).where(
            Booking.customer_id == user_id, Booking.rating != None
        )
    )

    hours = await db.execute(
        select(func.sum(Booking.working_hours)).where(
            Booking.customer_id == user_id,
            Booking.status == "completed",
        )
    )

    return {
        "active_bookings": active.scalar() or 0,
        "past_sessions": past.scalar() or 0,
        "rating_given": round(rating.scalar() or 0, 1),
        "hours_of_care": round(hours.scalar() or 0, 1),
    }


# ================= ADD RATING =================
async def add_rating(booking_id, rating, db):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None

    booking.rating = rating
    await db.commit()

    return booking


# ================= AVAILABLE =================
async def get_available_bookings(worker_id, db):
    result = await db.execute(select(Booking))
    return result.scalars().all()


# ================= ACCEPT =================
async def accept_booking(booking_id, worker_id, db):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None, "Booking not found"

    booking.worker_id = worker_id
    booking.status = "accepted"

    await db.commit()
    return booking, "Accepted"


# ================= START (OTP VERIFY) =================
async def start_work(booking_id, otp, db):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None, "Booking not found"

    if booking.start_otp != otp:
        return None, "Invalid OTP"

    booking.status = "started"
    booking.start_time = datetime.utcnow()

    await db.commit()
    return booking, "Started"


# ================= END =================
async def end_work(booking_id, db):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None, "Booking not found"

    booking.end_time = datetime.utcnow()
    diff = booking.end_time - booking.start_time

    booking.working_hours = round(diff.total_seconds() / 3600, 2)
    booking.end_otp = generate_otp()
    booking.status = "waiting_for_verification"

    await db.commit()
    return booking, "Ended"


# ================= VERIFY END OTP =================
async def verify_end_otp(booking_id, otp, db):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None, "Booking not found"

    if booking.end_otp != otp:
        return None, "Invalid OTP"

    booking.status = "completed"
    await db.commit()

    return booking, "Completed"


# ================= FINAL AMOUNT =================
async def get_final_amount(booking_id, db):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None

    return {"total_amount": booking.total_amount}


# ================= LIST BOOKINGS =================
async def list_bookings(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    service_type: str = None,
    selected_service: str = None,
):
    query = select(Booking)

    # ✅ FILTER: service_type
    if service_type:
        query = query.where(Booking.service_type == service_type)

    # ✅ FILTER: selected_services (JSON contains)
    if selected_service:
        query = query.where(Booking.selected_services.contains([selected_service]))

    # ✅ COUNT TOTAL
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    # ✅ PAGINATION
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    bookings = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "data": bookings,
    }


# ================= GET BOOKING BY ID =================
async def get_booking_by_id(booking_id: int, db: AsyncSession):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    return result.scalar_one_or_none()
