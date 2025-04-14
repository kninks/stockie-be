from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Stock
from app.modules.ml_ops.schemas.metadata_schema import (
    ModelMetadataResponseSchema,
    SaveModelMetadataRequestSchema,
)
from app.modules.ml_ops.services.metadata_service import (
    MetadataService,
    get_metadata_service,
)


class MetadataController:
    def __init__(self, service: MetadataService):
        self.service = service

    async def insert_stock_controller(
        self,
        db: AsyncSession,
        stock_ticker: str,
        industry_code: IndustryCodeEnum,
        stock_name: str,
        stock_description: Optional[str] = None,
    ):
        try:
            response: Stock = await self.service.insert_stock(
                db=db,
                stock_ticker=stock_ticker,
                industry_code=industry_code,
                stock_name=stock_name,
                stock_description=stock_description,
            )
            return jsonable_encoder(response)
        except Exception as e:
            raise e

    async def update_stock_controller(
        self,
        db: AsyncSession,
        stock_ticker: str,
        industry_code: Optional[IndustryCodeEnum] = None,
        stock_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        stock_description: Optional[str] = None,
    ) -> Stock:
        try:
            response = await self.service.update_stock(
                db=db,
                stock_ticker=stock_ticker,
                industry_code=industry_code,
                stock_name=stock_name,
                is_active=is_active,
                stock_description=stock_description,
            )
            return jsonable_encoder(response)
        except Exception as e:
            raise e

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
    ):
        try:
            response = await self.service.save_stock_model(
                stock_ticker=request.stock_ticker,
                version=request.version,
                accuracy=request.accuracy,
                model_path=request.model_path,
                scaler_path=request.scaler_path,
                features_used=request.features_used,
                additional_data=request.additional_data,
                db=db,
            )
            return jsonable_encoder(response)
        except Exception as e:
            raise e


def get_metadata_controller() -> MetadataController:
    return MetadataController(service=get_metadata_service())
