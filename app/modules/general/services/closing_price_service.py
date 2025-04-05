import logging
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List

from fastapi import Depends
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
from app.models import ClosingPrice
from app.modules.general.repositories.closing_price_repository import (
    ClosingPriceRepository,
)

logger = logging.getLogger(__name__)


class ClosingPriceService:
    def __init__(
        self,
        closing_price_repository: ClosingPriceRepository = Depends(
            ClosingPriceRepository
        ),
    ):
        self.closing_price_repo = closing_price_repository

    async def get_by_stock_ticker_and_date_range(
        self,
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> List[ClosingPrice]:
        validate_required(stock_ticker, "stock ticker")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            prices = await self.closing_price_repo.fetch_by_stock_ticker_and_date_range(
                db=db,
                stock_ticker=stock_ticker,
                target_date=target_date,
                days_back=days_back,
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch closing prices for ticker '{stock_ticker}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch closing prices") from e

        validate_entity_exists(prices, f"Closing prices for {stock_ticker}")
        validate_exact_length(prices, days_back, f"closing prices for {stock_ticker}")
        return prices

    async def get_by_stock_tickers_and_date_range(
        self,
        db: AsyncSession,
        stock_tickers: List[str],
        target_date: date,
        days_back: int,
    ) -> Dict[str, List[ClosingPrice]]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                prices = (
                    await self.closing_price_repo.fetch_by_stock_ticker_and_date_range(
                        db=db,
                        stock_ticker=stock_tickers[0],
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
            else:
                prices = (
                    await self.closing_price_repo.fetch_by_stock_tickers_and_date_range(
                        db=db,
                        stock_tickers=stock_tickers,
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch closing prices for tickers '{stock_tickers}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch closing prices") from e

        validate_entity_exists(prices, "Closing prices")
        expected_total = len(stock_tickers) * days_back
        validate_exact_length(prices, expected_total, "closing prices")

        grouped: Dict[str, List[ClosingPrice]] = defaultdict(list)
        for price in prices:
            grouped[price.stock_ticker].append(price)

        return dict(grouped)

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
            prices = await self.closing_price_repo.fetch_closing_price_values_by_stock_ticker_and_date_range(
                db=db,
                stock_ticker=stock_tickers[0],
                target_date=target_date,
                days_back=days_back,
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch closing prices for ticker '{stock_ticker}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch closing prices") from e

        validate_entity_exists(prices, "Closing prices")
        validate_exact_length(prices, days_back, "closing prices")
        return prices

    async def get_closing_price_value_by_stock_tickers_and_date_range(
        self,
        db: AsyncSession,
        stock_tickers: List[str],
        target_date: date,
        days_back: int,
    ) -> Dict[str, List[float]]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                prices = (
                    await self.closing_price_repo.fetch_by_stock_ticker_and_date_range(
                        db=db,
                        stock_ticker=stock_tickers[0],
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
            else:
                prices = (
                    await self.closing_price_repo.fetch_by_stock_tickers_and_date_range(
                        db=db,
                        stock_tickers=stock_tickers,
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch closing prices for tickers '{stock_tickers}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch closing prices") from e

        validate_entity_exists(prices, "Closing prices")
        expected_total = len(stock_tickers) * days_back
        validate_exact_length(prices, expected_total, "closing prices")

        grouped: Dict[str, List[float]] = defaultdict(list)
        for price in prices:
            grouped[price.stock_ticker].append(price.closing_price)

        return dict(grouped)

    async def create_one(self, db: AsyncSession, price_data: dict) -> ClosingPrice:
        validate_required(price_data, "closing price data")

        try:
            price_data["stock_ticker"] = normalize_stock_ticker(
                price_data["stock_ticker"]
            )
            price = await self.closing_price_repo.create_one(
                db=db, price_data=price_data
            )
        except DBError:
            raise
        except Exception as e:
            logger.error(f"Unexpected DB error during create_one: {e}")
            raise DBError("Unexpected error while creating closing price") from e

        logger.info(
            f"Inserted closing price for {price.stock_ticker} on {price.target_date}."
        )
        return price

    async def create_multiple(
        self, db: AsyncSession, price_data_list: List[dict]
    ) -> List[ClosingPrice]:
        validate_required(price_data_list, "closing price data list")
        try:
            price_data_list = normalize_stock_tickers_in_data(price_data_list)
            prices = await self.closing_price_repo.create_multiple(
                db=db, price_data_list=price_data_list
            )
        except DBError:
            raise
        except Exception as e:
            logger.error(f"Unexpected DB error during create_multiple: {e}")
            raise DBError("Unexpected error while creating closing prices") from e

        logger.info(f"Inserted {len(price_data_list)} closing prices.")
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
            deleted_count = await self.closing_price_repo.delete_older_than(
                db=db, cutoff_date=cutoff_date
            )
        except Exception as e:
            logger.error(
                f"Failed to delete closing prices older than {cutoff_date}: {e}"
            )
            raise DBError("Failed to delete old closing prices") from e

        logger.info(f"Deleted {deleted_count} closing prices before {cutoff_date}")
        return deleted_count
