import logging
from datetime import date, timedelta

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import (
    validate_entity_exists,
    validate_enum_input,
    validate_required,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import TopPrediction
from app.modules.general.repositories.top_prediction_repository import (
    TopPredictionRepository,
)

logger = logging.getLogger(__name__)


class TopPredictionService:
    def __init__(
        self,
        top_prediction_repository: TopPredictionRepository = Depends(
            TopPredictionRepository
        ),
    ):
        self.top_prediction_repo = top_prediction_repository

    async def get_by_industry_code_and_target_date_and_period(
        self,
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        period: int,
    ) -> TopPrediction:
        validate_required(industry_code, "industry code")
        validate_enum_input(industry_code, IndustryCodeEnum, "industry code")
        validate_required(target_date, "target date")
        validate_required(period, "period")

        try:
            top_prediction = await self.top_prediction_repo.fetch_by_industry_code_and_target_date_and_period(
                db=db,
                industry_code=industry_code,
                target_date=target_date,
                period=period,
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch top prediction for industry_code={industry_code}, "
                f"target_date={target_date}, period={period}: {e}"
            )
            raise DBError("Failed to fetch top prediction") from e

        validate_entity_exists(
            top_prediction,
            f"Top prediction for industry code '{industry_code}', target date {target_date}, and period {period}",
        )
        return top_prediction

    async def create(
        self,
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        period: int,
    ) -> TopPrediction:
        validate_required(industry_code, "industry code")
        validate_enum_input(industry_code, IndustryCodeEnum, "industry code")
        validate_required(target_date, "target date")
        validate_required(period, "period")

        existing = await self.top_prediction_repo.fetch_by_industry_code_and_target_date_and_period(
            db=db,
            industry_code=industry_code,
            target_date=target_date,
            period=period,
        )
        if existing:
            raise DBError(
                "Top prediction already exists for given industry/date/period"
            )

        try:
            top_prediction = await self.top_prediction_repo.create_one(
                db=db,
                industry_code=industry_code,
                target_date=target_date,
                period=period,
            )
        except Exception as e:
            logger.error(
                f"Failed to create top prediction for industry_code={industry_code}, "
                f"target_date={target_date}, period={period}: {e}"
            )
            raise DBError("Failed to create top prediction") from e

        return top_prediction

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
            deleted_count = await self.top_prediction_repo.delete_older_than(
                db=db, cutoff_date=cutoff_date
            )
        except Exception as e:
            logger.error(
                f"Failed to delete top predictions older than {cutoff_date}: {e}"
            )
            raise DBError("Failed to delete old top predictions") from e

        logger.info(f"Deleted {deleted_count} top predictions older than {cutoff_date}")
        return deleted_count
