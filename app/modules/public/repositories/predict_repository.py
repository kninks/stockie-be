from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction, TopPrediction
from app.modules.public.schema.predict_schema import (
    TopPredictionRankSchema,
)


class PredictRepository:
    """Handles database operations related to stock predictions."""

    @staticmethod
    async def fetch_top_prediction(
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        period: int,
        target_date: date,
    ) -> List[TopPredictionRankSchema]:
        stmt = (
            select(
                Prediction.rank,
                Prediction.stock_ticker,
                Prediction.predicted_price,
                Prediction.closing_price,
            )
            .select_from(TopPrediction)
            .join(Prediction)
            .where(
                TopPrediction.industry_code == industry_code,
                TopPrediction.period == period,
                TopPrediction.target_date == target_date,
            )
            .order_by(Prediction.rank)
            # .options(joinedload(TopPrediction.top_ranks))
        )

        result = await db.execute(stmt)
        top_prediction_rows = result.fetchall()

        top_prediction = [
            TopPredictionRankSchema(
                rank=row[0],
                ticker=row[1],
                predicted_price=row[2],
                closing_price=row[3],
            )
            for row in top_prediction_rows
        ]

        return top_prediction

    # @staticmethod
    # async def save_top_prediction(
    #     db: AsyncSession,
    #     industry_id: int,
    #     period: int,
    #     target_date: date,
    #     ranked_predictions: List[RankedPrediction],
    # ) -> bool:
    #     top_prediction = TopPrediction(
    #         industry_id=industry_id,
    #         period=period,
    #         target_date=target_date,
    #     )
    #     db.add(top_prediction)
    #     await db.flush()
    #
    #     for rp in ranked_predictions:
    #         db.add(
    #             TopPredictionRank(
    #                 top_prediction_id=top_prediction.id,
    #                 prediction_id=rp.prediction.id,
    #                 rank=rp.rank,
    #             )
    #         )
    #
    #     await db.commit()
    #     await db.refresh(top_prediction)
    #     if top_prediction:
    #         for rank in top_prediction.top_ranks:
    #             await db.refresh(rank)
    #         return True
    # return False
