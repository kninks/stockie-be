import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.general.services.industry_service import (
    IndustryService,
    get_industry_service,
)
from app.api.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.api.general.services.top_prediction_service import (
    TopPredictionService,
    get_top_prediction_service,
)
from app.api.public.repositories.predict_repository import (
    PredictRepository,
)
from app.api.public.schema.predict_schema import (
    GetTopPredictionResponseSchema,
)
from app.core.common.exceptions.custom_exceptions import DBError, ResourceNotFoundError

# from app.core.common.utils.datetime_utils import get_today_bangkok_date
from app.core.enums.industry_code_enum import IndustryCodeEnum

logger = logging.getLogger(__name__)


class PredictService:
    def __init__(
        self,
        predict_repo: PredictRepository,
        industry_service: IndustryService,
        prediction_service: PredictionService,
        top_prediction_service: TopPredictionService,
    ):
        self.predict_repo = predict_repo
        self.industry_service = industry_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service

    async def get_top_prediction(
        self, industry: IndustryCodeEnum, period: int, db: AsyncSession
    ) -> GetTopPredictionResponseSchema:
        # target_date: date = get_today_bangkok_date()
        target_date = date(2025, 4, 18)  # temporary

        try:
            top_prediction = await self.predict_repo.fetch_top_prediction(
                db=db,
                industry_code=industry,
                period=period,
                target_date=target_date,
            )

            if not top_prediction:
                logger.error("No top prediction found.")
                raise ResourceNotFoundError("No top prediction found.")

            return GetTopPredictionResponseSchema(ranked_predictions=top_prediction)
        except Exception as e:
            logger.error(f"Failed to get top prediction from database: {e}")
            raise DBError("Failed to get top prediction from database") from e


def get_predict_service() -> PredictService:
    return PredictService(
        predict_repo=PredictRepository(),
        industry_service=get_industry_service(),
        prediction_service=get_prediction_service(),
        top_prediction_service=get_top_prediction_service(),
    )
