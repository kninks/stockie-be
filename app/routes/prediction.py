from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.prediction_schema import PredictionQuerySchema
from app.services.database import get_db

router = APIRouter()


@router.get("/prediction")
async def fetch_predictions(
        industry: str,
        period: int,
        db: AsyncSession = Depends(get_db())
):
    query_params = PredictionQuerySchema(industry=industry, period=period)
    # predictions = await get_predictions(db, query_params)
    return {"message": "predictions"}