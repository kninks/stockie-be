from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.database import get_db

router = APIRouter()

@router.get("/test-db")
async def test_db_endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"test_result": result.scalar()}