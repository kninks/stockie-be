from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.controllers.metadata_controller import (
    MetadataController,
    get_metadata_controller,
)
from app.api.internal.schemas.metadata_schema import (
    ModelMetadataResponseSchema,
    SaveModelMetadataRequestSchema,
)
from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.db_session import get_db
from app.core.enums.industry_code_enum import IndustryCodeEnum

router = APIRouter(
    prefix="/metadata",
    tags=["[Internal] Metadata"],
)


@router.post("/stock/insert")
async def insert_stock_route(
    stock_ticker: str,
    industry_code: IndustryCodeEnum,
    stock_name: str,
    stock_description: str | None = None,
    controller: MetadataController = Depends(get_metadata_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.insert_stock_controller(
        db=db,
        stock_ticker=stock_ticker,
        industry_code=industry_code,
        stock_name=stock_name,
        stock_description=stock_description,
    )
    return success_response(data=response)


@router.patch("/stock/update")
async def update_stock_route(
    stock_ticker: str,
    industry_code: IndustryCodeEnum | None = None,
    stock_name: str | None = None,
    is_active: bool | None = None,
    stock_description: str | None = None,
    controller: MetadataController = Depends(get_metadata_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.update_stock_controller(
        db=db,
        stock_ticker=stock_ticker,
        industry_code=industry_code,
        stock_name=stock_name,
        is_active=is_active,
        stock_description=stock_description,
    )
    return success_response(data=response)


@router.get(
    "/ml-model", response_model=BaseSuccessResponse[list[ModelMetadataResponseSchema]]
)
async def get_model_metadata_route(
    stock_tickers: list[str] = Query(...),
    controller: MetadataController = Depends(get_metadata_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[ModelMetadataResponseSchema] = await controller.get_model_controller(
        stock_tickers=stock_tickers, db=db
    )
    return success_response(data=response)


@router.post("/ml-model")
async def insert_model_metadata_route(
    request: SaveModelMetadataRequestSchema,
    controller: MetadataController = Depends(get_metadata_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.save_model_controller(
        request=request,
        db=db,
    )
    return success_response(data=response)
