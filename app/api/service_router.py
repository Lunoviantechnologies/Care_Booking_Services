from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.service_schema import ServiceCreate
from app.services.service_service import *

router = APIRouter(prefix="/api/services", tags=["Services"])


# ✅ CREATE
@router.post("/create")
async def create(data: ServiceCreate, db: AsyncSession = Depends(get_db)):
    return await create_service(data, db)


# ✅ GET ALL
@router.get("/get-all")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await get_services(db)


# ✅ GET ONE
@router.get("/get-one/{service_id}")
async def get_one(service_id: int, db: AsyncSession = Depends(get_db)):
    service = await get_service(service_id, db)
    if not service:
        raise HTTPException(404, "Not found")
    return service


# ✅ UPDATE
@router.put("/update/{service_id}")
async def update(
    service_id: int, data: ServiceCreate, db: AsyncSession = Depends(get_db)
):
    service = await update_service(service_id, data, db)
    if not service:
        raise HTTPException(404, "Not found")
    return {"message": "Updated"}


# ✅ DELETE
@router.delete("/delete/{service_id}")
async def delete(service_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_service(service_id, db)
    if not success:
        raise HTTPException(404, "Not found")
    return {"message": "Deleted"}
