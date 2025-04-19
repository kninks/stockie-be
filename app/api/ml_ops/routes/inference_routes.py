from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.ml_ops.controllers.inference_controller import (
    InferenceController,
    get_inference_controller,
)
from app.api.ml_ops.schemas.inference_schema import (
    InferenceResultSchema,
    StockToPredictRequestSchema,
    TriggerAllInferenceRequestSchema,
    TriggerInferenceRequestSchema,
)
from app.core.common.utils.datetime_utils import get_today_bangkok_date
from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.db_session import get_db
from app.core.enums.industry_code_enum import IndustryCodeEnum

router = APIRouter(
    # prefix="/inference",
    tags=["[ml-ops] Inference"],
)


@router.post("/trigger-infer-and-save/industry")
async def trigger_infer_and_save_industry_route(
    request: TriggerAllInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.infer_and_save_industry_controller(request=request, db=db)
    return success_response(data=None)


@router.post("/trigger-infer-and-save/stocks")
async def trigger_infer_and_save_route(
    request: TriggerInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.infer_and_save(request=request, db=db)
    return success_response(data=None)


@router.post(
    "/trigger-infer/industry",
    response_model=BaseSuccessResponse[list[InferenceResultSchema]],
)
async def trigger_infer_only_industry_route(
    request: TriggerAllInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[InferenceResultSchema] = (
        await controller.infer_only_industry_controller(request=request, db=db)
    )
    return success_response(data=response)


@router.post(
    "/trigger-infer/stocks",
    response_model=BaseSuccessResponse[list[InferenceResultSchema]],
)
async def trigger_infer_only_route(
    request: TriggerInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[InferenceResultSchema] = await controller.infer_only_controller(
        request=request, db=db
    )
    return success_response(data=response)


@router.get(
    "/inference_data/industry",
    response_model=BaseSuccessResponse[list[StockToPredictRequestSchema]],
)
async def get_inference_data_industry_route(
    industry: IndustryCodeEnum = Query(...),
    target_date: date = Query(default=get_today_bangkok_date()),
    days_back: int = Query(default=60, ge=1),
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[StockToPredictRequestSchema] = (
        await controller.get_inference_data_industry_controller(
            industry=industry,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
    )
    return success_response(data=response)


@router.get(
    "/inference_data/stocks",
    response_model=BaseSuccessResponse[list[StockToPredictRequestSchema]],
)
async def get_inference_data_route(
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(default=60, ge=1),
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[StockToPredictRequestSchema] = (
        await controller.get_inference_data_by_stock_tickers_controller(
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
    )
    return success_response(data=response)
