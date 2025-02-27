from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.prediction_model import PredictionResult

async def get_prediction_results(db: AsyncSession, filters: dict):
    query = select(PredictionResult).where(
        PredictionResult.industry == filters["industry"],
        PredictionResult.created_at >= filters["start_date"],
        PredictionResult.created_at <= filters["end_date"]
    )

    result = await db.execute(query)
    return result.scalars().all()