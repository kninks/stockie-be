import logging
from datetime import date

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import sanitize_batch
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction, TopPrediction

logger = logging.getLogger(__name__)


class ProcessDataRepository:
    @staticmethod
    async def create_top_prediction_and_update_ranks(
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        period: int,
        target_date: date,
        ranked_updates: list[dict],
    ) -> int:
        try:
            top_prediction = TopPrediction(
                industry_code=industry_code,
                target_date=target_date,
                period=period,
            )
            db.add(top_prediction)
            await db.flush()

            sanitized = sanitize_batch(
                ranked_updates, allowed_fields={"prediction_id", "rank"}
            )
            logger.debug(f"Sanitized ranked updates: {sanitized}")
            bound_data = [
                {
                    "id": item["prediction_id"],
                    "rank": item["rank"],
                    "top_prediction_id": top_prediction.id,
                }
                for item in sanitized
            ]

            stmt = update(Prediction)
            await db.execute(stmt, bound_data)
            await db.commit()
            return len(bound_data)

        except Exception as e:
            logger.error(f"Failed to batch update predictions: {e}")
            await db.rollback()
            raise DBError("Batch update failed") from e
