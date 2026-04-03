
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.pricing import Pricing


# ================= CREATE PRICING =================
async def create_pricing(data, db: AsyncSession):
    """
    Create new pricing entry
    """
    pricing = Pricing(**data.dict())

    db.add(pricing)
    await db.commit()
    await db.refresh(pricing)

    return pricing


# ================= GET PRICING =================
async def get_pricing(service_type, duration, persons, db: AsyncSession):
    """
    Get price based on service, duration, and persons
    """
    result = await db.execute(
        select(Pricing).where(
            Pricing.service_type == service_type, Pricing.duration == duration
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


# ================= GET ALL PRICING =================
async def get_all_pricing(db: AsyncSession):
    """
    Get all pricing records
    """
    result = await db.execute(select(Pricing))
    return result.scalars().all()


# ================= UPDATE PRICING =================
async def update_pricing(pricing_id, data, db: AsyncSession):
    """
    Update pricing record
    """
    result = await db.execute(select(Pricing).where(Pricing.id == pricing_id))
    pricing = result.scalar_one_or_none()

    if not pricing:
        return None

    pricing.service_type = data.service_type
    pricing.duration = data.duration
    pricing.price = data.price
    pricing.min_persons = data.min_persons
    pricing.max_persons = data.max_persons

    await db.commit()
    await db.refresh(pricing)

    return pricing


# ================= DELETE PRICING =================
async def delete_pricing(pricing_id, db: AsyncSession):
    """
    Delete pricing record
    """
    result = await db.execute(select(Pricing).where(Pricing.id == pricing_id))
    pricing = result.scalar_one_or_none()

    if not pricing:
        return False

    await db.delete(pricing)
    await db.commit()

    return True
