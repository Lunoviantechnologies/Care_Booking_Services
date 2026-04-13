from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import Base, engine, AsyncSessionLocal
from app.api import booking_router, pricing_router, service_router

# ✅ IMPORT BOTH SEEDS
from app.db.seed.seed_pricing import seed_pricing
from app.db.seed.service_seed import seed_services


# ================= LIFESPAN =================
@asynccontextmanager
async def lifespan(app: FastAPI):

    # 🔥 CREATE TABLES
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 🔥 SEED DATA
    async with AsyncSessionLocal() as db:
        print("🚀 Seeding pricing data...")
        await seed_pricing(db)

        print("🚀 Seeding service data...")
        await seed_services(db)

    yield  # app runs here

    # (optional shutdown)


# ================= APP =================
app = FastAPI(lifespan=lifespan)


# ================= ROUTERS =================
app.include_router(booking_router.router)
app.include_router(pricing_router.router)
app.include_router(service_router.router)


# ================= ROOT =================
@app.get("/")
async def root():
    return {"message": "Care Booking Service Running 🚀"}
