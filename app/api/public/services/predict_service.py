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
from app.core.common.utils.datetime_utils import (
    get_last_market_open_date,
    get_n_market_days_ahead,
    get_yesterday_bangkok_date,
    is_market_closed,
)
from app.core.common.utils.validators import validate_required
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
        yesterday: date = get_yesterday_bangkok_date()
        validate_required(industry, "industry")
        validate_required(period, "period")

        closing_price_date = (
            get_last_market_open_date(yesterday)
            if is_market_closed(yesterday)
            else yesterday
        )
        predicted_price_date = get_n_market_days_ahead(
            start_date=closing_price_date, n=period + 1
        )

        try:
            top_prediction = await self.predict_repo.fetch_top_prediction(
                db=db,
                industry_code=industry,
                period=period,
                target_date=closing_price_date,
            )

            if not top_prediction:
                logger.error("No top prediction found.")
                raise ResourceNotFoundError("No top prediction found.")

            return GetTopPredictionResponseSchema(
                ranked_predictions=top_prediction,
                closing_price_date=closing_price_date,
                predicted_price_date=predicted_price_date,
            )

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
