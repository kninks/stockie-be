from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Prediction, Stock, TopPrediction, TopPredictionRank
from app.modules.top_prediction.schema.top_prediction_api_schema import (
    TopPredictionRankSchema,
)
from app.modules.top_prediction.services.types.ranked_prediction import RankedPrediction


class TopPredictionRepository:
    """Handles database operations related to stock predictions."""

    @staticmethod
    async def fetch_top_prediction_from_db(
        db: AsyncSession,
        industry_id: int,
        period: int,
        target_date: date,
    ) -> list[TopPredictionRankSchema]:
        stmt = (
            select(
                TopPredictionRank.rank,
                Stock.ticker,
                Prediction.predicted_price,
                Prediction.actual_price,
            )
            .select_from(TopPrediction)
            .join(TopPredictionRank)
            .join(Prediction)
            .join(Stock, Stock.id == Prediction.stock_id)
            .where(
                TopPrediction.industry_id == industry_id,
                TopPrediction.period == period,
                TopPrediction.target_date == target_date,
            )
            # .options(joinedload(TopPrediction.top_ranks))
        )

        result = await db.execute(stmt)
        top_prediction_rows = result.fetchall()

        top_prediction = [
            TopPredictionRankSchema(
                rank=row[0],
                ticker=row[1],
                predicted_price=row[2],
                actual_price=row[3],
            )
            for row in top_prediction_rows
        ]

        return top_prediction

    @staticmethod
    async def save_top_prediction(
        db: AsyncSession,
        industry_id: int,
        period: int,
        target_date: date,
        ranked_predictions: List[RankedPrediction],
    ) -> None:
        top_prediction = TopPrediction(
            industry_id=industry_id,
            period=period,
            target_date=target_date,
        )
        db.add(top_prediction)
        await db.flush()

        for rp in ranked_predictions:
            db.add(
                TopPredictionRank(
                    top_prediction_id=top_prediction.id,
                    prediction_id=rp.prediction.id,
                    rank=rp.rank,
                )
            )

        await db.commit()
        await db.refresh(top_prediction)
