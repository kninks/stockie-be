from datetime import date
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import TopPrediction


class TopPredictionRepository:
    @staticmethod
    async def fetch_by_industry_code_and_target_date_and_period(
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        period: int,
    ) -> Optional[TopPrediction]:
        stmt = select(TopPrediction).where(
            TopPrediction.industry_code == industry_code,
            TopPrediction.target_date == target_date,
            TopPrediction.period == period,
        )
        result = await db.execute(stmt)
        top_prediction = result.scalar_one_or_none()
        return top_prediction

    @staticmethod
    async def create_one(
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        period: int,
    ) -> TopPrediction:
        top_prediction = TopPrediction(
            industry_code=industry_code,
            target_date=target_date,
            period=period,
        )
        db.add(top_prediction)
        await db.flush()
        await db.commit()
        return top_prediction

    # TODO: fix warning?
    @staticmethod
    async def delete_older_than(db: AsyncSession, cutoff_date: date) -> int:
        stmt = (
            delete(TopPrediction)
            .where(TopPrediction.target_date < cutoff_date)
            .execution_options(synchronize_session=False)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
