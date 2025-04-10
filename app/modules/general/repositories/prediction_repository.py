import logging
from datetime import date
from typing import Set

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import sanitize_batch
from app.models import Prediction, Stock

logger = logging.getLogger(__name__)


class PredictionRepository:
    ALLOWED_FIELDS: Set[str] = {
        "stock_ticker",
        "model_id",
        "target_date",
        "period",
        "predicted_price",
        "closing_price",
        "trading_data_id",
        "rank",
        "top_prediction_id",
    }

    @staticmethod
    async def fetch_by_id(db: AsyncSession, prediction_id: int) -> Prediction:
        stmt = select(Prediction).where(Prediction.id == prediction_id)
        result = await db.execute(stmt)
        prediction = result.scalar_one_or_none()
        return prediction

    @staticmethod
    async def fetch_by_ids(
        db: AsyncSession, prediction_ids: list[int]
    ) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.id.in_(prediction_ids))
            .order_by(Prediction.stock_ticker, Prediction.period)
        )
        result = await db.execute(stmt)
        predictions: list[Prediction] = list(result.scalars().all())
        return predictions

    @staticmethod
    async def fetch_by_date_and_period_and_stock_ticker(
        db: AsyncSession,
        target_date: date,
        period: int,
        stock_ticker: str,
    ) -> Prediction:
        stmt = (
            select(Prediction)
            .where(
                Prediction.target_date == target_date,
                Prediction.period == period,
                Prediction.stock_ticker == stock_ticker,
            )
            .order_by(Prediction.stock_ticker, Prediction.period)
        )
        result = await db.execute(stmt)
        prediction = result.scalar_one_or_none()
        return prediction

    @staticmethod
    async def fetch_by_date_and_period_and_stock_tickers(
        db: AsyncSession,
        target_date: date,
        period: int,
        stock_tickers: list[str],
    ) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .where(
                Prediction.target_date == target_date,
                Prediction.period == period,
                Prediction.stock_ticker.in_(stock_tickers),
            )
            .order_by(Prediction.stock_ticker, Prediction.period)
        )
        result = await db.execute(stmt)
        predictions: list[Prediction] = list(result.scalars().all())
        return predictions

    @staticmethod
    async def fetch_by_date_and_period_and_industry_code(
        db: AsyncSession,
        target_date: date,
        period: int,
        industry_code: str,
    ) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .join(Stock)
            .where(
                Prediction.target_date == target_date,
                Prediction.period == period,
                Stock.industry_code == industry_code,
            )
        ).order_by(Prediction.stock_ticker, Prediction.period)
        result = await db.execute(stmt)
        predictions: list[Prediction] = list(result.scalars().all())
        return predictions

    @staticmethod
    async def fetch_by_date_and_period_and_industry_codes(
        db: AsyncSession,
        target_date: date,
        period: int,
        industry_codes: list[str],
    ) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .join(Stock)
            .where(
                Prediction.target_date == target_date,
                Prediction.period == period,
                Stock.industry_code.in_(industry_codes),
            )
            .order_by(Prediction.stock_ticker, Prediction.period)
        )
        result = await db.execute(stmt)
        predictions: list[Prediction] = list(result.scalars().all())
        return predictions

    @staticmethod
    async def create_one(
        db: AsyncSession,
        prediction_data: dict,
        refresh: bool = True,
    ) -> Prediction:
        sanitized_data = sanitize_batch(
            [prediction_data], allowed_fields=PredictionRepository.ALLOWED_FIELDS
        )[0]
        try:
            prediction = Prediction(**sanitized_data)
            db.add(prediction)
            await db.flush()
            await db.commit()
            if refresh:
                await db.refresh(prediction)
            return prediction
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create prediction: {e}")
            raise DBError("Failed to create prediction") from e

    @staticmethod
    async def create_multiple(
        db: AsyncSession,
        prediction_data_list: list[dict],
        refresh: bool = True,
    ) -> list[Prediction]:
        sanitized_data_list = sanitize_batch(
            prediction_data_list, allowed_fields=PredictionRepository.ALLOWED_FIELDS
        )
        try:
            predictions = [Prediction(**data) for data in sanitized_data_list]
            db.add_all(predictions)
            await db.flush()
            await db.commit()
            if refresh:
                for p in predictions:
                    await db.refresh(p)
            return predictions
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create multiple predictions: {e}")
            raise DBError("Failed to create predictions") from e

    # TODO
    @staticmethod
    async def delete_older_than(db: AsyncSession, cutoff_date: date) -> int:
        try:
            stmt = (
                delete(Prediction)
                .where(Prediction.target_date < cutoff_date)
                .execution_options(synchronize_session=False)
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to delete predictions older than {cutoff_date}: {e}")
            raise DBError("Failed to delete old predictions") from e
