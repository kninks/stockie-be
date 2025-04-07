import logging
from typing import Optional

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.models import StockModel

logger = logging.getLogger(__name__)


class ModelMetadataRepository:
    @staticmethod
    async def update_and_create_model_metadata(
        db: AsyncSession,
        stock_ticker: str,
        version: str,
        accuracy: float,
        model_path: str,
        scaler_path: str,
        additional_data: Optional[dict] = None,
    ) -> StockModel:
        try:
            await db.execute(
                update(StockModel)
                .where(StockModel.stock_ticker == stock_ticker)
                .values(is_active=False)
            )

            new_model = StockModel(
                stock_ticker=stock_ticker,
                version=version,
                accuracy=accuracy,
                model_path=model_path,
                scaler_path=scaler_path,
                additional_data=additional_data,
                is_active=True,
            )
            db.add(new_model)
            await db.flush()
            await db.commit()

            return new_model
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to save StockModel for {stock_ticker}: {e}")
            raise DBError("Failed to save stock model") from e
