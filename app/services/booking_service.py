import random
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.booking import Booking
from app.db.models.pricing import Pricing
import httpx


# ================= OTP =================
def generate_otp() -> str:
    return str(random.randint(1000, 9999))


# ================= PRICE =================
async def get_price_from_db(
    service_type: str, duration: int, persons: int, db: AsyncSession
) -> Optional[float]:

    result = await db.execute(
        select(Pricing).where(
            func.lower(Pricing.service_type) == service_type.lower(),
            Pricing.duration == duration,
        )
    )

    pricing_list = result.scalars().all()

    for p in pricing_list:
        if p.min_persons and persons < p.min_persons:
            continue
        if p.max_persons and persons > p.max_persons:
            continue
        return p.price

    return None


# ================= TRANSPORT =================
def calculate_transport_fee(distance_km: float) -> int:
    if distance_km <= 5:
        return 0
    elif distance_km <= 10:
        return 29
    return 49


# ================= EXTRA =================
def calculate_extra_charges(
    is_peak: bool, is_emergency: bool, is_subscription: bool, distance_km: float
) -> Dict[str, Any]:

    base_extra = 49
    convenience_fee = 0 if is_subscription else 29
    transport_fee = calculate_transport_fee(distance_km)

    peak_charge = 50 if is_peak else 0
    emergency_charge = 100 if is_emergency else 0

    total_extra = (
        base_extra + convenience_fee + transport_fee + peak_charge + emergency_charge
    )

    return {
        "base_extra": base_extra,
        "convenience_fee": convenience_fee,
        "transport_fee": transport_fee,
        "peak_charge": peak_charge,
        "emergency_charge": emergency_charge,
        "total_extra": total_extra,
    }


# ================= TOTAL (NO COMMISSION) =================
def calculate_total(base_price: float, extra: float) -> float:
    return round(base_price + extra, 2)


# ================= CREATE =================
async def create_booking(
    data, db: AsyncSession
) -> Optional[Tuple[Booking, Dict[str, Any]]]:

    base_price = await get_price_from_db(
        data.service_type, data.duration, data.persons, db
    )

    if base_price is None:
        return None

    extra_data = calculate_extra_charges(
        data.is_peak, data.is_emergency, data.is_subscription, data.distance_km
    )

    total = calculate_total(base_price, extra_data["total_extra"])

    booking = Booking(
        service_type=data.service_type.lower(),
        duration=data.duration,
        persons=data.persons,
        base_price=base_price,
        extra_charges=extra_data["total_extra"],
        total_amount=total,
        status="pending",
        start_otp=generate_otp(),
        distance_km=data.distance_km,
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    return booking, extra_data


# ================= WORKER SERVICE =================
async def get_worker(worker_id: int) -> Optional[dict]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"http://worker-service/api/worker/{worker_id}")
            if res.status_code == 200:
                return res.json()
    except Exception:
        return None
    return None


# ================= ELIGIBILITY =================
def is_worker_eligible(worker: dict, booking: Booking) -> bool:

    if worker.get("status") != "approved":
        return False

    if worker.get("availability") != "online":
        return False

    if booking.service_type == "baby_care":
        return worker.get("gender") == "female" and 20 <= worker.get("age", 0) <= 45

    if booking.service_type == "pregnancy_care":
        return worker.get("gender") == "female" and 23 <= worker.get("age", 0) <= 50

    if booking.service_type in ["kitchen_work", "elder_care", "party_help"]:
        return 18 <= worker.get("age", 0) <= 60

    return False


# ================= AVAILABLE BOOKINGS =================
async def get_available_bookings(worker_id: int, db: AsyncSession):

    worker = await get_worker(worker_id)

    if not worker:
        return {"message": "Worker not found"}

    result = await db.execute(
        select(Booking).where(Booking.status == "pending", Booking.worker_id == None)
    )

    bookings = result.scalars().all()

    return [b for b in bookings if is_worker_eligible(worker, b)]


# ================= ACCEPT =================
async def accept_booking(booking_id: int, worker_id: int, db: AsyncSession):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None, "Booking not found"

    if booking.status != "pending":
        return None, "Already accepted"

    worker = await get_worker(worker_id)
    if not worker:
        return None, "Worker not found"

    booking.worker_id = worker_id
    booking.status = "accepted"

    await db.commit()

    return booking, "Accepted"


# ================= START =================
async def start_work(booking_id: int, otp: str, db: AsyncSession):

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
async def end_work(booking_id: int, db: AsyncSession):

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

    return booking, "End OTP Generated"


# ================= VERIFY (NO COMMISSION) =================
async def verify_end_otp(booking_id: int, otp: str, db: AsyncSession):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None, "Booking not found"

    if booking.end_otp != otp:
        return None, "Invalid OTP"

    price_per_hour = booking.base_price / booking.duration
    new_base = price_per_hour * booking.working_hours

    booking.total_amount = round(new_base + booking.extra_charges, 2)
    booking.status = "completed"

    await db.commit()

    return booking, "Completed"


# ================= FINAL =================
async def get_final_amount(booking_id: int, db: AsyncSession):

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        return None

    return {"total_amount": booking.total_amount}
