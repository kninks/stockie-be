from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ml_ops.schemas.model_metadata_schema import (
    ModelMetadataResponseSchema,
    SaveModelMetadataRequestSchema,
)
from app.modules.ml_ops.services.model_metadata_service import ModelMetadataService


class ModelMetadataController:
    def __init__(self, service: ModelMetadataService = Depends(ModelMetadataService)):
        self.service = service

    async def get_model_controller(
        self,
        stock_tickers: list[str],
        db: AsyncSession,
    ) -> list[ModelMetadataResponseSchema]:
        try:
            response = await self.service.get_stock_model(
                stock_tickers=stock_tickers, db=db
            )
            return response
        except Exception as e:
            raise e

    async def save_model_controller(
        self,
        request: SaveModelMetadataRequestSchema,
        db: AsyncSession,
    ) -> None:
        try:
            response = await self.service.save_stock_model(
                stock_ticker=request.stock_ticker,
                version=request.version,
                accuracy=request.accuracy,
                model_path=request.model_path,
                scaler_path=request.scaler_path,
                additional_data=request.additional_data,
                db=db,
            )
            return response
        except Exception as e:
            raise e
