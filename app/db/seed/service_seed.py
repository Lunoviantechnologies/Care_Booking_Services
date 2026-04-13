from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.service import Service, ServiceOption, ServiceField


async def seed_services(db: AsyncSession):

    # Check if already seeded
    result = await db.execute(select(Service))
    existing = result.scalars().first()

    if existing:
        print("✅ Services already seeded")
        return

    print("🚀 Seeding default services...")

    services_data = [
        {
            "key": "baby_care",
            "title": "Baby Care",
            "color": "#F8BBD0",
            "options": [
                "Holding and comforting the baby",
                "Burping baby after feeding",
                "Rocking baby to sleep",
                "Diaper changing",
                "Cleaning baby after urination/soiling",
                "Swaddling",
                "Monitoring baby while parents rest",
            ],
            "fields": [
                {"field_name": "baby_age", "field_type": "number"},
                {"field_name": "special_instructions", "field_type": "text"},
            ],
        },
        {
            "key": "pet_care",
            "title": "Pet Care",
            "color": "#FFE082",
            "options": [
                "Feeding pets",
                "Refilling water",
                "Pet supervision",
                "Playing with pets",
                "Cleaning feeding bowls",
                "Cleaning minor pet mess",
                "Short supervised walks",
            ],
            "fields": [
                {"field_name": "pet_type", "field_type": "dropdown"},
                {"field_name": "pet_name", "field_type": "text"},
            ],
        },
        {
            "key": "elder_care",
            "title": "Elder Care",
            "color": "#D1C4E9",
            "options": [
                "Medication reminders",
                "Mobility assistance",
                "Meal preparation",
                "Companionship",
            ],
            "fields": [
                {"field_name": "medical_conditions", "field_type": "text"},
            ],
        },
        {
            "key": "pregnancy_care",
            "title": "Pregnancy Care",
            "color": "#FFCC80",
            "options": [
                "Routine check support",
                "Diet monitoring",
                "Light exercise help",
            ],
            "fields": [
                {"field_name": "trimester", "field_type": "number"},
            ],
        },
        {
            "key": "home_assistance",
            "title": "Home Assistance",
            "color": "#C8E6C9",
            "options": [
                "Cooking",
                "Cleaning",
                "Laundry",
                "Dishwashing",
            ],
            "fields": [],
        },
    ]

    for s in services_data:

        service = Service(key=s["key"], title=s["title"], color=s["color"])

        db.add(service)
        await db.flush()

        # add options
        for opt in s["options"]:
            db.add(ServiceOption(service_id=service.id, name=opt))

        # add fields
        for f in s["fields"]:
            db.add(
                ServiceField(
                    service_id=service.id,
                    field_name=f["field_name"],
                    field_type=f["field_type"],
                )
            )

    await db.commit()

    print("✅ Seeding completed")
