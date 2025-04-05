from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.db_session import get_db
from app.modules.ml_ops.controllers.model_metadata_controller import (
    ModelMetadataController,
)
from app.modules.ml_ops.schemas.model_metadata_schema import (
    ModelMetadataResponseSchema,
    SaveModelMetadataRequestSchema,
)

router = APIRouter(
    prefix="/model-metadata",
    tags=["Model Metadata"],
)


@router.get("", response_model=BaseSuccessResponse[list[ModelMetadataResponseSchema]])
async def get_model_metadate_route(
    stock_tickers: list[str] = Query(...),
    controller: ModelMetadataController = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the active model detail for the given stock ids.
    """
    response: list[ModelMetadataResponseSchema] = await controller.get_model_controller(
        stock_tickers=stock_tickers, db=db
    )
    return success_response(data=response)


@router.post("", response_model=BaseSuccessResponse[None])
async def save_model_metadata_route(
    request: SaveModelMetadataRequestSchema,
    controller: ModelMetadataController = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Save the model for the given stock ids.
    """
    await controller.save_model_controller(
        request=request,
        db=db,
    )
    return success_response()
