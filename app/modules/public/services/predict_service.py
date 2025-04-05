import logging
from datetime import date

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError, ResourceNotFoundError
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction
from app.modules.general.services.industry_service import IndustryService
from app.modules.general.services.prediction_service import PredictionService
from app.modules.general.services.top_prediction_service import TopPredictionService
from app.modules.public.repositories.predict_repository import (
    PredictRepository,
)
from app.modules.public.schema.predict_schema import (
    PredictRequestSchema,
    PredictResponseSchema,
)
from app.modules.public.services.types.ranked_prediction import RankedPrediction

logger = logging.getLogger(__name__)


class PredictService:
    def __init__(
        self,
        top_prediction_repo: PredictRepository = Depends(PredictRepository),
        industry_service: IndustryService = Depends(IndustryService),
        prediction_service: PredictionService = Depends(PredictionService),
        top_prediction_service: TopPredictionService = Depends(TopPredictionService),
    ):
        self.top_prediction_repo = top_prediction_repo
        self.industry_service = industry_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service

    async def get_top_prediction(
        self, industry: IndustryCodeEnum, period: int, db: AsyncSession
    ) -> PredictResponseSchema:
        # target_date = date.today()
        target_date = date(2025, 3, 28)  # temporary
        try:
            top_prediction = await self.top_prediction_repo.fetch_top_prediction(
                db=db,
                industry_code=IndustryCodeEnum(industry),
                period=period,
                target_date=target_date,
            )

            if not top_prediction:
                logger.error("No top prediction found.")
                raise ResourceNotFoundError("No top prediction found.")

            return PredictResponseSchema(ranked_stocks=top_prediction)
        except Exception as e:
            logger.error(f"Failed to get top prediction from database: {e}")
            raise DBError("Failed to get top prediction from database") from e

    # TODO: move to ml-ops / internal / general
    async def calculate_and_save_top_prediction(
        self, request: PredictRequestSchema, db: AsyncSession
    ) -> None:
        # target_date = date.today()
        target_date = date(2025, 3, 28)  # temporary
        predictions = (
            await self.prediction_service.get_by_date_and_period_and_industry_code(
                db=db,
                target_date=target_date,
                period=request.period,
                industry_code=request.industry,
            )
        )

        ranked_predictions = self.rank_prediction(predictions)
        try:
            top_prediction = await self.top_prediction_service.create(
                db=db,
                industry_code=request.industry,
                target_date=target_date,
                period=request.period,
            )

            updates = [
                {
                    "id": rp.prediction.id,
                    "rank": rp.rank,
                    "top_prediction_id": top_prediction.id,
                }
                for rp in ranked_predictions
            ]

            await self.prediction_service.update_batch_rank_and_top_prediction(
                db=db,
                updates=updates,
            )

        except Exception as e:
            logger.error(f"Failed to calculate and save top prediction: {e}")
            raise DBError("Failed to save top prediction") from e

    @staticmethod
    def rank_prediction(predictions: list[Prediction]) -> list[RankedPrediction]:
        predictions.sort(
            key=lambda x: x.predicted_price / x.closing_price if x.closing_price else 0,
            reverse=True,
        )
        ranked_predictions = [
            RankedPrediction(prediction=p, rank=i + 1)
            for i, p in enumerate(predictions[:5])
        ]
        return ranked_predictions
