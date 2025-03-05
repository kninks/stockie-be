import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test-log")
async def test_log():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    return {"test_result": "done"}

@router.get("/test-db")
async def test_db_endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"test_result": result.scalar()}