import logging
from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import sanitize_batch
from app.models import TradingData

logger = logging.getLogger(__name__)


class TradingDataRepository:
    ALLOWED_FIELDS = {
        "stock_ticker",
        "target_date",
        "close",
        "open",
        "high",
        "low",
        "volumes",
    }

    @staticmethod
    async def fetch_by_stock_ticker_and_date_range(
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> list[TradingData]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(TradingData)
            .where(
                TradingData.stock_ticker == stock_ticker,
                TradingData.target_date.between(start_date, target_date),
            )
            .order_by(TradingData.target_date.asc())
        )

        result = await db.execute(stmt)
        trading_data_list: list[TradingData] = list(result.scalars().all())
        return trading_data_list

    @staticmethod
    async def fetch_by_stock_tickers_and_date_range(
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[TradingData]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(TradingData)
            .where(
                TradingData.stock_ticker.in_(stock_tickers),
                TradingData.target_date.between(start_date, target_date),
            )
            .order_by(TradingData.stock_ticker, TradingData.target_date.asc())
        )

        result = await db.execute(stmt)
        trading_data_list: list[TradingData] = list(result.scalars().all())
        return trading_data_list

    @staticmethod
    async def fetch_closing_price_values_by_stock_ticker_and_date_range(
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> list[float]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(TradingData.close)
            .where(
                TradingData.stock_ticker == stock_ticker,
                TradingData.target_date.between(start_date, target_date),
            )
            .order_by(TradingData.target_date.asc())
        )

        result = await db.execute(stmt)
        closing_prices_list: list[float] = list(result.scalars().all())
        return closing_prices_list

    @staticmethod
    async def create_one(db: AsyncSession, trading_data: dict) -> TradingData:
        sanitized_data = sanitize_batch(
            [trading_data], allowed_fields=TradingDataRepository.ALLOWED_FIELDS
        )[0]
        try:
            trading_data = TradingData(**sanitized_data)
            db.add(trading_data)
            await db.flush()
            await db.commit()
            await db.refresh(trading_data)
            return trading_data
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create trading data: {e}")
            raise DBError("Failed to create trading data") from e

    @staticmethod
    async def create_multiple(
        db: AsyncSession, trading_data_list: list[dict]
    ) -> list[TradingData]:
        sanitized_data_list = sanitize_batch(
            trading_data_list, allowed_fields=TradingDataRepository.ALLOWED_FIELDS
        )
        try:
            trading_data_list = [TradingData(**data) for data in sanitized_data_list]
            db.add_all(trading_data_list)
            await db.flush()
            await db.commit()
            for cp in trading_data_list:
                await db.refresh(cp)
            return trading_data_list
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create multiple trading data: {e}")
            raise DBError("Failed to create trading data") from e

    # TODO: fix warning?
    @staticmethod
    async def delete_older_than(db: AsyncSession, cutoff_date: date) -> int:
        try:
            stmt = (
                delete(TradingData)
                .where(TradingData.target_date < cutoff_date)
                .execution_options(synchronize_session=False)
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to delete trading data older than {cutoff_date}: {e}")
            raise DBError("Failed to delete old trading data") from e
