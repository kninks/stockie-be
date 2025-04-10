import logging
from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import sanitize_batch
from app.models import Feature

logger = logging.getLogger(__name__)


class FeatureRepository:
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
    ) -> list[Feature]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(Feature)
            .where(
                Feature.stock_ticker == stock_ticker,
                Feature.target_date.between(start_date, target_date),
            )
            .order_by(Feature.target_date.asc())
        )

        result = await db.execute(stmt)
        features_list: list[Feature] = list(result.scalars().all())
        return features_list

    @staticmethod
    async def fetch_by_stock_tickers_and_date_range(
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[Feature]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(Feature)
            .where(
                Feature.stock_ticker.in_(stock_tickers),
                Feature.target_date.between(start_date, target_date),
            )
            .order_by(Feature.stock_ticker, Feature.target_date.asc())
        )

        result = await db.execute(stmt)
        features_list: list[Feature] = list(result.scalars().all())
        return features_list

    @staticmethod
    async def fetch_closing_price_values_by_stock_ticker_and_date_range(
        db: AsyncSession,
        stock_ticker: str,
        target_date: date,
        days_back: int,
    ) -> list[float]:
        start_date = target_date - timedelta(days=days_back)

        stmt = (
            select(Feature.close)
            .where(
                Feature.stock_ticker == stock_ticker,
                Feature.target_date.between(start_date, target_date),
            )
            .order_by(Feature.target_date.asc())
        )

        result = await db.execute(stmt)
        closing_prices_list: list[float] = list(result.scalars().all())
        return closing_prices_list

    @staticmethod
    async def create_one(db: AsyncSession, feature_data: dict) -> Feature:
        sanitized_data = sanitize_batch(
            [feature_data], allowed_fields=FeatureRepository.ALLOWED_FIELDS
        )[0]
        try:
            features = Feature(**sanitized_data)
            db.add(features)
            await db.flush()
            await db.commit()
            await db.refresh(features)
            return features
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create features: {e}")
            raise DBError("Failed to create features") from e

    @staticmethod
    async def create_multiple(
        db: AsyncSession, feature_data_list: list[dict]
    ) -> list[Feature]:
        sanitized_data_list = sanitize_batch(
            feature_data_list, allowed_fields=FeatureRepository.ALLOWED_FIELDS
        )
        try:
            features_list = [Feature(**data) for data in sanitized_data_list]
            db.add_all(features_list)
            await db.flush()
            await db.commit()
            for cp in features_list:
                await db.refresh(cp)
            return features_list
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create multiple features: {e}")
            raise DBError("Failed to create features") from e

    # TODO: fix warning?
    @staticmethod
    async def delete_older_than(db: AsyncSession, cutoff_date: date) -> int:
        try:
            stmt = (
                delete(Feature)
                .where(Feature.target_date < cutoff_date)
                .execution_options(synchronize_session=False)
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to delete features older than {cutoff_date}: {e}")
            raise DBError("Failed to delete old features") from e
