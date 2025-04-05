import logging
from datetime import date, timedelta
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError, ResourceNotFoundError
from app.core.common.utils.validators import (
    normalize_stock_ticker,
    normalize_stock_tickers,
    normalize_stock_tickers_in_data,
    validate_entity_exists,
    validate_enum_input,
    validate_exact_length,
    validate_required,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction
from app.modules.general.repositories.prediction_repository import PredictionRepository
from app.modules.general.services.closing_price_service import ClosingPriceService

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(
        self,
        prediction_repository: PredictionRepository = Depends(PredictionRepository),
        closing_price_service: ClosingPriceService = Depends(ClosingPriceService),
    ):
        self.prediction_repo = prediction_repository
        self.closing_price_service = closing_price_service

    async def get_by_id(self, db: AsyncSession, prediction_id: int) -> Prediction:
        validate_required(prediction_id, "prediction ID")

        try:
            prediction = await self.prediction_repo.fetch_by_id(
                db=db, prediction_id=prediction_id
            )
        except Exception as e:
            logger.error(f"Failed to fetch prediction with ID {prediction_id}: {e}")
            raise DBError("Failed to fetch prediction") from e

        validate_entity_exists(prediction, f"Prediction {prediction_id}")
        return prediction

    async def get_by_ids(
        self, db: AsyncSession, prediction_ids: List[int]
    ) -> List[Prediction]:
        validate_required(prediction_ids, "prediction IDs")

        try:
            if len(prediction_ids) == 1:
                prediction = await self.prediction_repo.fetch_by_id(
                    db=db, prediction_id=prediction_ids[0]
                )
                predictions = [prediction] if prediction else []
            else:
                predictions = await self.prediction_repo.fetch_by_ids(
                    db=db, prediction_ids=prediction_ids
                )
        except Exception as e:
            logger.error(f"Failed to fetch prediction with IDs {prediction_ids}: {e}")
            raise DBError("Failed to fetch prediction") from e

        validate_entity_exists(predictions, f"Predictions for IDs {prediction_ids}")
        validate_exact_length(predictions, len(prediction_ids), "predictions")
        return predictions

    async def get_by_date_and_period_and_stock_ticker(
        self,
        db: AsyncSession,
        target_date: date,
        period: int,
        stock_ticker: str,
    ) -> Prediction:
        validate_required(stock_ticker, "stock ticker")
        validate_required(target_date, "target date")
        validate_required(period, "period")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            prediction = (
                await self.prediction_repo.fetch_by_date_and_period_and_stock_ticker(
                    db=db,
                    target_date=target_date,
                    period=period,
                    stock_ticker=stock_ticker,
                )
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch prediction for stock {stock_ticker} on {target_date}, period {period}: {e}"
            )
            raise DBError("Failed to fetch prediction") from e

        validate_entity_exists(
            prediction,
            f"Prediction with date {target_date}, period {period}, and stock {stock_ticker}",
        )
        return prediction

    async def get_by_date_and_period_and_stock_tickers(
        self,
        db: AsyncSession,
        target_date: date,
        period: int,
        stock_tickers: List[str],
    ) -> List[Prediction]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")
        validate_required(period, "period")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                prediction = await self.prediction_repo.fetch_by_date_and_period_and_stock_ticker(
                    db=db,
                    target_date=target_date,
                    period=period,
                    stock_ticker=stock_tickers[0],
                )
                predictions = [prediction] if prediction else []
            else:
                predictions = await self.prediction_repo.fetch_by_date_and_period_and_stock_tickers(
                    db=db,
                    target_date=target_date,
                    period=period,
                    stock_tickers=stock_tickers,
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch predictions for stock tickers {stock_tickers} on {target_date}, period {period}: {e}"
            )
            raise DBError("Failed to fetch predictions") from e

        validate_entity_exists(
            predictions,
            f"Predictions with date {target_date}, period {period}, and stock tickers {stock_tickers}",
        )
        validate_exact_length(predictions, len(stock_tickers), "predictions")
        return predictions

    async def get_by_date_and_period_and_industry_code(
        self,
        db: AsyncSession,
        target_date: date,
        period: int,
        industry_code: str,
    ) -> List[Prediction]:
        validate_required(industry_code, "industry code")
        validate_enum_input(industry_code, IndustryCodeEnum, "industry code")
        validate_required(target_date, "target date")
        validate_required(period, "period")

        try:
            predictions = (
                await self.prediction_repo.fetch_by_date_and_period_and_industry_code(
                    db=db,
                    target_date=target_date,
                    period=period,
                    industry_code=industry_code,
                )
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch predictions for industry {industry_code} on {target_date}, period {period}: {e}"
            )
            raise DBError("Failed to fetch predictions") from e

        validate_entity_exists(
            predictions,
            f"Predictions with date {target_date}, period {period}, and industry code {industry_code}",
        )
        validate_exact_length(
            predictions, 5, f"predictions for industry code '{industry_code}'"
        )
        return predictions

    async def get_by_date_and_period_and_industry_codes(
        self,
        db: AsyncSession,
        target_date: date,
        period: int,
        industry_codes: List[str],
    ) -> List[Prediction]:
        validate_required(industry_codes, "industry codes")
        validate_enum_input(industry_codes, IndustryCodeEnum, "industry codes")
        validate_required(target_date, "target date")
        validate_required(period, "period")

        try:
            if len(industry_codes) == 1:
                prediction = await self.prediction_repo.fetch_by_date_and_period_and_industry_code(
                    db=db,
                    target_date=target_date,
                    period=period,
                    industry_code=industry_codes[0],
                )
                predictions = [prediction] if prediction else []
            else:
                predictions = await self.prediction_repo.fetch_by_date_and_period_and_industry_codes(
                    db=db,
                    target_date=target_date,
                    period=period,
                    industry_codes=industry_codes,
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch predictions for industry codes {industry_codes} on {target_date}, period {period}: {e}"
            )
            raise DBError("Failed to fetch predictions") from e

        validate_entity_exists(
            predictions,
            f"Predictions with date {target_date}, period {period}, and industry codes {industry_codes}",
        )
        validate_exact_length(predictions, 5 * len(industry_codes), "predictions")
        return predictions

    async def create_by_list(
        self,
        db: AsyncSession,
        prediction_data_list: List[dict],
        refresh: bool = True,
    ) -> List[Prediction]:
        validate_required(prediction_data_list, "prediction data")
        prediction_data_list = normalize_stock_tickers_in_data(prediction_data_list)

        try:
            prediction_data_list = normalize_stock_tickers_in_data(prediction_data_list)
            if len(prediction_data_list) == 1:
                prediction = await self.prediction_repo.create_one(
                    db=db, prediction_data=prediction_data_list[0], refresh=refresh
                )
                predictions = [prediction] if prediction else []
            else:
                predictions = await self.prediction_repo.create_multiple(
                    db=db, prediction_data_list=prediction_data_list, refresh=refresh
                )
        except Exception as e:
            logger.error(f"Failed to create predictions: {e}")
            raise DBError("Failed to create predictions") from e

        validate_entity_exists(predictions, "Predictions")
        validate_exact_length(predictions, len(prediction_data_list), "predictions")
        return predictions

    async def update_rank_and_top_id(
        self,
        db: AsyncSession,
        prediction_id: int,
        rank: int | None,
        top_prediction_id: int | None,
    ) -> None:
        validate_required(prediction_id, "prediction ID")

        try:
            updated_count = await self.prediction_repo.update_rank_and_top_id(
                db=db,
                prediction_id=prediction_id,
                rank=rank,
                top_prediction_id=top_prediction_id,
            )
        except Exception as e:
            logger.error(f"Failed to update prediction ID {prediction_id}: {e}")
            raise DBError("Failed to update prediction") from e

        if updated_count == 0:
            logger.warning(f"No prediction updated for ID {prediction_id}")
            raise ResourceNotFoundError(f"Prediction {prediction_id} not found")

    async def update_batch_rank_and_top_prediction(
        self, db: AsyncSession, updates: List[dict]
    ) -> int:
        """
        updates with a list of {id, rank, top_prediction_id}
        """
        validate_required(updates, "prediction updates")
        for item in updates:
            validate_required(item.get("id"), "prediction ID")

        try:
            if len(updates) == 1:
                prediction = await self.prediction_repo.update_rank_and_top_id(
                    db=db,
                    prediction_id=updates[0]["id"],
                    rank=updates[0]["rank"],
                    top_prediction_id=updates[0]["top_prediction_id"],
                )
                updated_count = 1 if prediction else 0
            else:
                updated_count = (
                    await self.prediction_repo.update_batch_rank_and_top_prediction(
                        db=db,
                        updates=updates,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to update prediction ranks and top prediction links: {e}"
            )
            raise DBError("Failed to update predictions") from e

        logger.info(f"Updated {updated_count} predictions.")
        return updated_count

    async def delete_older_than(
        self,
        db: AsyncSession,
        target_date: date,
        days_back: int,
    ) -> int:
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")

        cutoff_date = target_date - timedelta(days=days_back)

        try:
            deleted_count = await self.prediction_repo.delete_older_than(
                db=db, cutoff_date=cutoff_date
            )
        except Exception as e:
            logger.error(f"Failed to delete predictions older than {cutoff_date}: {e}")
            raise DBError("Failed to delete old predictions") from e

        logger.info(f"Deleted {deleted_count} predictions older than {cutoff_date}")
        return deleted_count
