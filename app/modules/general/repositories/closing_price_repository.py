import logging
from datetime import date, timedelta
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import sanitize_batch
from app.models import ClosingPrice

logger = logging.getLogger(__name__)


class ClosingPriceRepository:
    ALLOWED_FIELDS = {
        "stock_ticker",
        "target_date",
        "closing_price",
    }

    @staticmethod
    async def fetch_by_stock_ticker_and_date_range(
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> List[ClosingPrice]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(ClosingPrice)
            .where(
                ClosingPrice.stock_ticker == stock_ticker,
                ClosingPrice.target_date.between(start_date, target_date),
            )
            .order_by(ClosingPrice.target_date.asc())
        )

        result = await db.execute(stmt)
        closing_prices: List[ClosingPrice] = list(result.scalars().all())
        return closing_prices

    @staticmethod
    async def fetch_by_stock_tickers_and_date_range(
        db: AsyncSession,
        stock_tickers: List[str],
        target_date: date,
        days_back: int,
    ) -> List[ClosingPrice]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(ClosingPrice)
            .where(
                ClosingPrice.stock_ticker.in_(stock_tickers),
                ClosingPrice.target_date.between(start_date, target_date),
            )
            .order_by(ClosingPrice.stock_ticker, ClosingPrice.target_date)
        )

        result = await db.execute(stmt)
        closing_prices: List[ClosingPrice] = list(result.scalars().all())
        return closing_prices

    @staticmethod
    async def fetch_closing_price_values_by_stock_ticker_and_date_range(
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> List[float]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(ClosingPrice.closing_price)
            .where(
                ClosingPrice.stock_ticker == stock_ticker,
                ClosingPrice.target_date.between(start_date, target_date),
            )
            .order_by(ClosingPrice.target_date.asc())
        )

        result = await db.execute(stmt)
        closing_prices: List[float] = list(result.scalars().all())
        return closing_prices

    @staticmethod
    async def create_one(db: AsyncSession, price_data: dict) -> ClosingPrice:
        sanitized_data = sanitize_batch(
            [price_data], allowed_fields=ClosingPriceRepository.ALLOWED_FIELDS
        )[0]
        try:
            closing_price = ClosingPrice(**sanitized_data)
            db.add(closing_price)
            await db.flush()
            await db.commit()
            await db.refresh(closing_price)
            return closing_price
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create closing price: {e}")
            raise DBError("Failed to create closing price") from e

    @staticmethod
    async def create_multiple(
        db: AsyncSession, price_data_list: List[dict]
    ) -> List[ClosingPrice]:
        sanitized_data_list = sanitize_batch(
            price_data_list, allowed_fields=ClosingPriceRepository.ALLOWED_FIELDS
        )
        try:
            closing_prices = [ClosingPrice(**data) for data in sanitized_data_list]
            db.add_all(closing_prices)
            await db.flush()
            await db.commit()
            for cp in closing_prices:
                await db.refresh(cp)
            return closing_prices
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create multiple closing prices: {e}")
            raise DBError("Failed to create closing prices") from e

    # TODO: fix warning?
    @staticmethod
    async def delete_older_than(db: AsyncSession, cutoff_date: date) -> int:
        try:
            stmt = (
                delete(ClosingPrice)
                .where(ClosingPrice.target_date < cutoff_date)
                .execution_options(synchronize_session=False)
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(
                f"Failed to delete closing prices older than {cutoff_date}: {e}"
            )
            raise DBError("Failed to delete old closing prices") from e
