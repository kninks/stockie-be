import logging
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.general.services.stock_model_service import StockModelService
from app.modules.ml_ops.schemas.model_metadata_schema import (
    ModelMetadataResponseSchema,
)

logger = logging.getLogger(__name__)


class ModelMetadataService:
    def __init__(
        self,
        stock_model_service: StockModelService = Depends(StockModelService),
    ):
        self.stock_model_service = stock_model_service

    async def get_stock_model(
        self, stock_tickers: list[str], db: AsyncSession
    ) -> list[ModelMetadataResponseSchema]:
        models = await self.stock_model_service.get_active_by_stock_tickers(
            db=db, stock_tickers=stock_tickers
        )
        return [
            ModelMetadataResponseSchema(
                model_id=model.id,
                stock_ticker=model.stock_ticker,
                version=model.version,
                accuracy=model.accuracy,
                model_path=model.model_path,
                scaler_path=model.scaler_path,
                additional_data=model.additional_data,
            )
            for model in models
        ]

    # TODO: update previous model to inactive then save the new one
    async def save_stock_model(
        self,
        stock_ticker: str,
        version: str,
        accuracy: float,
        model_path: str,
        scaler_path: str,
        additional_data: Optional[dict],
        db: AsyncSession,
    ) -> None:
        pass
