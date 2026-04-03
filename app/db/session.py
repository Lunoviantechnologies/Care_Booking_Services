import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ IMPORTANT: force async driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

print("DATABASE_URL:", DATABASE_URL)


# ================= ENGINE =================
engine = create_async_engine(DATABASE_URL, echo=True)  # set False in production


# ================= SESSION =================
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# ================= BASE =================
Base = declarative_base()


# ================= DEPENDENCY =================
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
