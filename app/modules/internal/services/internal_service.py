import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import validate_required
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction
from app.modules.general.services.feature_service import (
    FeatureService,
    get_feature_service,
)
from app.modules.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.modules.general.services.stock_service import StockService, get_stock_service
from app.modules.general.services.top_prediction_service import (
    TopPredictionService,
    get_top_prediction_service,
)
from app.modules.internal.repositories.internal_repository import InternalRepository

logger = logging.getLogger(__name__)


class InternalService:
    def __init__(
        self,
        internal_repository: InternalRepository,
        stock_service: StockService,
        prediction_service: PredictionService,
        top_prediction_service: TopPredictionService,
        feature_service: FeatureService,
    ):
        self.internal_repository = internal_repository
        self.stock_service = stock_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service
        self.feature_service = feature_service

    async def rank_and_save_top_predictions_all(
        self,
        period: int,
        target_date: date,
        db: AsyncSession,
    ):
        validate_required(period, "period")
        validate_required(target_date, "target date")

        industry_codes = [item for item in IndustryCodeEnum]
        for industry_code in industry_codes:
            await self.rank_and_save_top_prediction(
                industry_code=industry_code,
                period=period,
                target_date=target_date,
                db=db,
            )

    async def rank_and_save_top_prediction(
        self,
        industry_code: IndustryCodeEnum,
        period: int,
        target_date: date,
        db: AsyncSession,
    ) -> None:
        validate_required(industry_code, "industry")
        validate_required(period, "period")
        validate_required(target_date, "target date")

        predictions = (
            await self.prediction_service.get_by_date_and_period_and_industry_code(
                db=db,
                target_date=target_date,
                period=period,
                industry_code=industry_code,
            )
        )

        ranked_predictions = self.rank_predictions(predictions)
        print(f"Ranked predictions: {ranked_predictions}")
        logger.info(f"Ranked predictions: {ranked_predictions}")

        # Save the ranked predictions to the database
        try:
            await self.internal_repository.create_top_prediction_and_update_ranks(
                db=db,
                industry_code=industry_code,
                target_date=target_date,
                period=period,
                ranked_updates=ranked_predictions,
            )
        except Exception as e:
            logger.error(f"Failed to save top prediction: {e}")
            raise DBError("Failed to save top prediction") from e

    # DONE
    @staticmethod
    def rank_predictions(predictions: list[Prediction]) -> list[dict]:
        predictions.sort(
            key=lambda x: x.predicted_price / x.closing_price if x.closing_price else 0,
            reverse=True,
        )
        ranked_predictions = [
            {
                "prediction_id": p.id,
                "rank": i + 1,
            }
            # RankedPrediction(prediction=p, rank=i + 1)
            for i, p in enumerate(predictions[:5])
        ]
        return ranked_predictions

    # TODO
    async def pull_features_all(self, target_date: date, db: AsyncSession) -> None:
        validate_required(target_date, "target date")
        stock_tickers = await self.stock_service.get_active_ticker_values(db=db)
        await self.pull_features(
            stock_tickers=stock_tickers, target_date=target_date, db=db
        )

    # TODO: scrape closing prices from Yahoo Finance -> validate -> save to DB
    async def pull_features(
        self, stock_tickers: list[str], target_date: date, db: AsyncSession
    ) -> None:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")

        # Assuming we have a function to fetch closing prices from an external API
        feature_list = [
            {
                "ticker": ticker,
                "target_date": target_date,
                "close": None,  # Placeholder for the actual closing price (float)
                "open": None,  # Placeholder for the actual opening price (float)
                "high": None,  # Placeholder for the actual high price (float)
                "low": None,  # Placeholder for the actual low price (float)
                "volumes": None,  # Placeholder for the actual volume (float)
            }
            for ticker in stock_tickers
        ]

        try:
            await self.feature_service.create_multiple(
                db=db,
                feature_data_list=feature_list,
            )
        except Exception as e:
            logger.error(f"Failed to pull closing prices: {e}")
            raise DBError("Failed to pull closing prices") from e


def get_internal_service() -> InternalService:
    return InternalService(
        internal_repository=InternalRepository(),
        stock_service=get_stock_service(),
        prediction_service=get_prediction_service(),
        top_prediction_service=get_top_prediction_service(),
        feature_service=get_feature_service(),
    )
