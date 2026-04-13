from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.service import Service, ServiceOption, ServiceField


# ✅ CREATE SERVICE
async def create_service(data, db: AsyncSession):

    service = Service(key=data.key, title=data.title, color=data.color)

    db.add(service)
    await db.flush()

    for opt in data.options:
        db.add(ServiceOption(service_id=service.id, name=opt.name))

    for field in data.fields:
        db.add(
            ServiceField(
                service_id=service.id,
                field_name=field.field_name,
                field_type=field.field_type,
            )
        )

    await db.commit()
    return service


# ✅ GET ALL SERVICES
async def get_services(db: AsyncSession):

    result = await db.execute(select(Service))
    services = result.scalars().all()

    response = []

    for s in services:
        response.append({"id": s.id, "key": s.key, "title": s.title, "color": s.color})

    return response


# ✅ GET SINGLE SERVICE
async def get_service(service_id: int, db: AsyncSession):

    result = await db.execute(select(Service).where(Service.id == service_id))
    s = result.scalar_one_or_none()

    if not s:
        return None

    return {
        "id": s.id,
        "key": s.key,
        "title": s.title,
        "color": s.color,
        "options": [o.name for o in s.options],
        "fields": [
            {"field_name": f.field_name, "field_type": f.field_type} for f in s.fields
        ],
    }


# ✅ UPDATE SERVICE
async def update_service(service_id, data, db: AsyncSession):

    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        return None

    service.key = data.key
    service.title = data.title
    service.color = data.color

    # delete old
    await db.execute(
        ServiceOption.__table__.delete().where(ServiceOption.service_id == service_id)
    )
    await db.execute(
        ServiceField.__table__.delete().where(ServiceField.service_id == service_id)
    )

    # add new
    for opt in data.options:
        db.add(ServiceOption(service_id=service_id, name=opt.name))

    for field in data.fields:
        db.add(
            ServiceField(
                service_id=service_id,
                field_name=field.field_name,
                field_type=field.field_type,
            )
        )

    await db.commit()
    return service


# ✅ DELETE SERVICE
async def delete_service(service_id, db: AsyncSession):

    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        return False

    await db.delete(service)
    await db.commit()

    return True
