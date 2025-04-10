import logging
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import (
    normalize_stock_ticker,
    normalize_stock_tickers,
    normalize_stock_tickers_in_data,
    validate_entity_exists,
    validate_exact_length,
    validate_required,
)
from app.models import Feature
from app.modules.general.repositories.feature_repository import (
    FeatureRepository,
)

logger = logging.getLogger(__name__)


class FeatureService:
    def __init__(
        self,
        feature_repository: FeatureRepository,
    ):
        self.feature_repo = feature_repository

    async def get_by_stock_ticker_and_date_range(
        self,
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> list[Feature]:
        validate_required(stock_ticker, "stock ticker")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            prices = await self.feature_repo.fetch_by_stock_ticker_and_date_range(
                db=db,
                stock_ticker=stock_ticker,
                target_date=target_date,
                days_back=days_back,
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch features for ticker '{stock_ticker}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch features") from e

        validate_entity_exists(prices, f"Features for {stock_ticker}")
        validate_exact_length(prices, days_back, f"features for {stock_ticker}")
        return prices

    async def get_by_stock_tickers_and_date_range(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[Feature]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                features = await self.feature_repo.fetch_by_stock_ticker_and_date_range(
                    db=db,
                    stock_ticker=stock_tickers[0],
                    target_date=target_date,
                    days_back=days_back,
                )
            else:
                features = (
                    await self.feature_repo.fetch_by_stock_tickers_and_date_range(
                        db=db,
                        stock_tickers=stock_tickers,
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch features for tickers '{stock_tickers}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch features") from e

        validate_entity_exists(features, "Features")
        expected_total = len(stock_tickers) * (days_back + 1)
        validate_exact_length(features, expected_total, "features")

        return features

    async def get_closing_price_value_by_stock_ticker_and_date_range(
        self,
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> list[float]:
        validate_required(stock_ticker, "stock ticker")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_tickers = normalize_stock_ticker(stock_ticker)

        try:
            prices = await self.feature_repo.fetch_closing_price_values_by_stock_ticker_and_date_range(
                db=db,
                stock_ticker=stock_tickers[0],
                target_date=target_date,
                days_back=days_back,
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch features for ticker '{stock_ticker}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch features") from e

        validate_entity_exists(prices, "Features")
        validate_exact_length(prices, days_back, "features")
        return prices

    async def get_closing_price_values_by_stock_tickers_and_date_range(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> dict[str, list[float]]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                feature_list = (
                    await self.feature_repo.fetch_by_stock_ticker_and_date_range(
                        db=db,
                        stock_ticker=stock_tickers[0],
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
            else:
                feature_list = (
                    await self.feature_repo.fetch_by_stock_tickers_and_date_range(
                        db=db,
                        stock_tickers=stock_tickers,
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch features for tickers '{stock_tickers}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch features") from e

        validate_entity_exists(feature_list, "Features")
        expected_total = len(stock_tickers) * (days_back + 1)
        validate_exact_length(feature_list, expected_total, "features")

        grouped: dict[str, list[float]] = defaultdict()
        for feature in feature_list:
            grouped[feature.stock_ticker].append(feature.close)

        return dict(grouped)

    async def create_one(self, db: AsyncSession, price_data: dict) -> Feature:
        validate_required(price_data, "features data")

        try:
            price_data["stock_ticker"] = normalize_stock_ticker(
                price_data["stock_ticker"]
            )
            price = await self.feature_repo.create_one(db=db, feature_data=price_data)
        except DBError:
            raise
        except Exception as e:
            logger.error(f"Unexpected DB error during create_one: {e}")
            raise DBError("Unexpected error while creating features") from e

        logger.info(
            f"Inserted feature for {price.stock_ticker} on {price.target_date}."
        )
        return price

    async def create_multiple(
        self, db: AsyncSession, feature_data_list: list[dict]
    ) -> list[Feature]:
        validate_required(feature_data_list, "feature data list")
        try:
            feature_data_list = normalize_stock_tickers_in_data(feature_data_list)
            prices = await self.feature_repo.create_multiple(
                db=db, feature_data_list=feature_data_list
            )
        except DBError:
            raise
        except Exception as e:
            logger.error(f"Unexpected DB error during create_multiple: {e}")
            raise DBError("Unexpected error while creating features") from e

        logger.info(f"Inserted {len(feature_data_list)} features.")
        return prices

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
            deleted_count = await self.feature_repo.delete_older_than(
                db=db, cutoff_date=cutoff_date
            )
        except Exception as e:
            logger.error(f"Failed to delete features older than {cutoff_date}: {e}")
            raise DBError("Failed to delete old features") from e

        logger.info(f"Deleted {deleted_count} features before {cutoff_date}")
        return deleted_count


def get_feature_service() -> FeatureService:
    return FeatureService(feature_repository=FeatureRepository())
