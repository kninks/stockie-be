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
from app.models import TradingData
from app.modules.general.repositories.trading_data_repository import (
    TradingDataRepository,
)

logger = logging.getLogger(__name__)


class TradingDataService:
    def __init__(
        self,
        trading_data_repository: TradingDataRepository,
    ):
        self.trading_data_repo = trading_data_repository

    async def get_by_stock_ticker_and_date_range(
        self,
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> list[TradingData]:
        validate_required(stock_ticker, "stock ticker")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            trading_data = (
                await self.trading_data_repo.fetch_by_stock_ticker_and_date_range(
                    db=db,
                    stock_ticker=stock_ticker,
                    target_date=target_date,
                    days_back=days_back,
                )
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch trading data for ticker '{stock_ticker}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch trading data") from e

        validate_entity_exists(trading_data, f"Trading data for {stock_ticker}")
        validate_exact_length(
            trading_data, days_back, f"trading data for {stock_ticker}"
        )
        return trading_data

    async def get_by_stock_tickers_and_date_range(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[TradingData]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")
        validate_required(days_back, "days back")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                trading_data_list = (
                    await self.trading_data_repo.fetch_by_stock_ticker_and_date_range(
                        db=db,
                        stock_ticker=stock_tickers[0],
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
            else:
                trading_data_list = (
                    await self.trading_data_repo.fetch_by_stock_tickers_and_date_range(
                        db=db,
                        stock_tickers=stock_tickers,
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch trading data for tickers '{stock_tickers}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch trading data") from e

        validate_entity_exists(trading_data_list, "Trading data")
        expected_total = len(stock_tickers) * (days_back + 1)
        validate_exact_length(trading_data_list, expected_total, "trading data")

        return trading_data_list

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
            prices = await self.trading_data_repo.fetch_closing_price_values_by_stock_ticker_and_date_range(
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

        validate_entity_exists(prices, "Trading data")
        validate_exact_length(prices, days_back, "trading data")
        return prices

    # FIXME: recheck
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
                trading_data_list = (
                    await self.trading_data_repo.fetch_by_stock_ticker_and_date_range(
                        db=db,
                        stock_ticker=stock_tickers[0],
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
            else:
                trading_data_list = (
                    await self.trading_data_repo.fetch_by_stock_tickers_and_date_range(
                        db=db,
                        stock_tickers=stock_tickers,
                        target_date=target_date,
                        days_back=days_back,
                    )
                )
        except Exception as e:
            logger.error(
                f"Failed to fetch trading data for tickers '{stock_tickers}', "
                f"target date '{target_date}', days back '{days_back}': {e}"
            )
            raise DBError("Failed to fetch trading data") from e

        validate_entity_exists(trading_data_list, "Trading data")
        expected_total = len(stock_tickers) * (days_back + 1)
        validate_exact_length(trading_data_list, expected_total, "trading data")

        grouped: dict[str, list[float]] = defaultdict()
        for trading_data in trading_data_list:
            grouped[trading_data.stock_ticker].append(trading_data.close)

        return dict(grouped)

    async def create_one(self, db: AsyncSession, trading_data: dict) -> TradingData:
        validate_required(trading_data, "trading data")

        try:
            trading_data["stock_ticker"] = normalize_stock_ticker(
                trading_data["stock_ticker"]
            )
            trading = await self.trading_data_repo.create_one(
                db=db, trading_data=trading_data
            )
        except DBError:
            raise
        except Exception as e:
            logger.error(f"Unexpected DB error during create_one: {e}")
            raise DBError("Unexpected error while creating trading data") from e

        logger.info(
            f"Inserted trading data for {trading.stock_ticker} on {trading.target_date}."
        )
        return trading

    async def create_multiple(
        self, db: AsyncSession, trading_data_dict_list: list[dict]
    ) -> list[TradingData]:
        validate_required(trading_data_dict_list, "trading data list")
        try:
            trading_data_dict_list = normalize_stock_tickers_in_data(
                trading_data_dict_list
            )
            trading_data_list = await self.trading_data_repo.create_multiple(
                db=db, trading_data_list=trading_data_dict_list
            )
        except DBError:
            raise
        except Exception as e:
            logger.error(f"Unexpected DB error during create_multiple: {e}")
            raise DBError("Unexpected error while creating trading data") from e

        logger.info(f"Inserted {len(trading_data_dict_list)} trading data.")
        return trading_data_list

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
            deleted_count = await self.trading_data_repo.delete_older_than(
                db=db, cutoff_date=cutoff_date
            )
        except Exception as e:
            logger.error(
                f"Failed to delete trading data  older than {cutoff_date}: {e}"
            )
            raise DBError("Failed to delete old trading data") from e

        logger.info(f"Deleted {deleted_count} trading data before {cutoff_date}")
        return deleted_count


def get_trading_data_service() -> TradingDataService:
    return TradingDataService(trading_data_repository=TradingDataRepository())
