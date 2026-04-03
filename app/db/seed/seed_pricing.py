# seed_pricing.py

from sqlalchemy.future import select
from app.db.models.pricing import Pricing


async def seed_pricing(db):
    """
    Seed initial pricing data (only if table is empty)
    """

    # ✅ CHECK IF DATA ALREADY EXISTS
    result = await db.execute(select(Pricing))
    existing = result.scalars().first()

    if existing:
        print("Pricing already exists ✅")
        return

    print("Seeding pricing data... 🚀")

    pricing_data = [
        #  Baby Care
        {"service_type": "baby_care", "duration": 1, "price": 349},
        {"service_type": "baby_care", "duration": 2, "price": 649},
        {"service_type": "baby_care", "duration": 4, "price": 1199},
        {"service_type": "baby_care", "duration": 8, "price": 1899},
        #  Pregnancy Care
        {"service_type": "pregnancy_care", "duration": 1, "price": 249},
        {"service_type": "pregnancy_care", "duration": 2, "price": 478},
        #  Pet Walking
        {"service_type": "pet_walking", "duration": 1, "price": 299},
        {"service_type": "pet_walking", "duration": 2, "price": 579},
        #  Kitchen Help
        {"service_type": "kitchen_work", "duration": 1, "price": 349, "max_persons": 4},
        {"service_type": "kitchen_work", "duration": 2, "price": 579, "max_persons": 4},
        {"service_type": "kitchen_work", "duration": 3, "price": 759, "max_persons": 4},
        #  Party Help
        {"service_type": "party_help", "duration": 5, "price": 1500, "max_persons": 10},
        {
            "service_type": "party_help",
            "duration": 5,
            "price": 2500,
            "min_persons": 11,
            "max_persons": 15,
        },
        #  Elder Care
        {"service_type": "elder_care", "duration": 1, "price": 399},
        {"service_type": "elder_care", "duration": 2, "price": 779},
        {"service_type": "elder_care", "duration": 4, "price": 1499},
        {"service_type": "elder_care", "duration": 8, "price": 1799},
    ]

    # ✅ INSERT DATA
    for item in pricing_data:
        db.add(Pricing(**item))

    # ✅ COMMIT ASYNC
    await db.commit()

    print("Pricing seeded successfully ✅")
