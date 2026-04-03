from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import Base, engine, AsyncSessionLocal
from app.api import booking_router, pricing_router
from app.db.seed.seed_pricing import seed_pricing


# ================= LIFESPAN (REPLACES on_event) =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 CREATE TABLES (ASYNC)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 🔥 SEED DATA
    print("Seeding pricing data... 🚀")

    async with AsyncSessionLocal() as db:
        await seed_pricing(db)

    yield  # app runs here

    # (optional shutdown logic here)


# ================= APP =================
app = FastAPI(lifespan=lifespan)


# ================= ROUTERS =================
app.include_router(booking_router.router)
app.include_router(pricing_router.router)


# ================= ROOT =================
@app.get("/")
async def root():
    return {"message": "Care Booking Service Running 🚀"}
