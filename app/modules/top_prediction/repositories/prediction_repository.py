from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.models import Prediction, Stock


class PredictionRepository:
    # def __init__(self, db: Session):
    #     self.db = db
    @staticmethod
    async def fetch_ranked_predictions(
        db: AsyncSession,
        industry_id: int,
        period: int,
        target_date: date,
    ) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .options(
                load_only(
                    Prediction.id,
                    Prediction.predicted_price,
                    Prediction.actual_price,
                )
            )
            .join(Stock)
            .where(
                Stock.industry_id == industry_id,
                Prediction.period == period,
                Prediction.target_date == target_date,
            )
            .order_by((Prediction.predicted_price / Prediction.actual_price).desc())
        )
        result = await db.execute(stmt)
        predictions: List[Prediction] = list(result.scalars().all())
        return predictions


prediction_repository = PredictionRepository()
