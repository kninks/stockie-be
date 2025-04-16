from datetime import date
from typing import List

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
from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.db_session import get_db
from app.core.enums.industry_code_enum import IndustryCodeEnum

router = APIRouter(
    prefix="/inference",
    tags=["[ml-ops] Inference"],
)


@router.post("/trigger-infer-and-save/industry")
async def trigger_infer_and_save_all_route(
    request: TriggerAllInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.infer_and_save_by_industry(request=request, db=db)
    return success_response(data=None)


@router.post("/trigger-infer-and-save/tickers")
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
async def trigger_infer_only_route_all(
    request: TriggerAllInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[InferenceResultSchema] = await controller.infer_only_by_industry(
        request=request, db=db
    )
    return success_response(data=response)


@router.post(
    "/trigger-infer/tickers",
    response_model=BaseSuccessResponse[list[InferenceResultSchema]],
)
async def trigger_infer_only_route(
    request: TriggerInferenceRequestSchema,
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[InferenceResultSchema] = await controller.infer_only(
        request=request, db=db
    )
    return success_response(data=response)


@router.get(
    "/inference_data/all",
    response_model=BaseSuccessResponse[list[StockToPredictRequestSchema]],
)
async def get_all_inference_data_route(
    controller: InferenceController = Depends(get_inference_controller),
    target_date: date = Query(...),
    days_back: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    response: list[StockToPredictRequestSchema] = (
        await controller.get_all_inference_data_controller(
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
    )
    return success_response(data=response)


@router.get(
    "/inference_data/industry",
    response_model=BaseSuccessResponse[list[StockToPredictRequestSchema]],
)
async def get_inference_data_by_industry_route(
    industry: IndustryCodeEnum = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    controller: InferenceController = Depends(get_inference_controller),
    db: AsyncSession = Depends(get_db),
):
    response: list[StockToPredictRequestSchema] = (
        await controller.get_inference_data_by_industry_controller(
            industry=industry,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
    )
    return success_response(data=response)


@router.get(
    "/inference_data",
    response_model=BaseSuccessResponse[list[StockToPredictRequestSchema]],
)
async def get_inference_data_route(
    stock_tickers: List[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
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
