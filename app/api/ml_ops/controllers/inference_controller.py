from datetime import date

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.ml_ops.schemas.inference_schema import (
    InferenceResultSummarySchema,
    StockToPredictRequestSchema,
    TriggerAllInferenceRequestSchema,
    TriggerInferenceRequestSchema,
)
from app.api.ml_ops.services.inference_service import (
    InferenceService,
    get_inference_service,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum


class InferenceController:
    def __init__(self, service: InferenceService):
        self.service = service

    async def infer_and_save_industry_controller(
        self,
        request: TriggerAllInferenceRequestSchema,
        db: AsyncSession,
    ) -> None:
        response = await self.service.run_and_save_inference_by_industry_code(
            target_date=request.target_date,
            industry_code=request.industry,
            days_back=request.days_back,
            days_forward=request.days_forward,
            periods=request.periods,
            db=db,
        )
        return response

    async def infer_and_save(
        self,
        request: TriggerInferenceRequestSchema,
        db: AsyncSession,
    ) -> None:
        response = await self.service.run_and_save_inference_by_stock_tickers(
            stock_tickers=request.stock_tickers,
            target_date=request.target_date,
            days_back=request.days_back,
            days_forward=request.days_forward,
            periods=request.periods,
            db=db,
        )
        return response

    async def infer_only_industry_controller(
        self,
        request: TriggerAllInferenceRequestSchema,
        db: AsyncSession,
    ) -> InferenceResultSummarySchema:
        response: InferenceResultSummarySchema = (
            await self.service.run_inference_by_industry_code(
                industry_code=request.industry,
                target_date=request.target_date,
                days_back=request.days_back,
                days_forward=request.days_forward,
                db=db,
            )
        )
        return jsonable_encoder(response)

    async def infer_only_controller(
        self,
        request: TriggerInferenceRequestSchema,
        db: AsyncSession,
    ) -> InferenceResultSummarySchema:
        response: InferenceResultSummarySchema = (
            await self.service.run_inference_by_stock_tickers(
                stock_tickers=request.stock_tickers,
                target_date=request.target_date,
                days_back=request.days_back,
                days_forward=request.days_forward,
                db=db,
            )
        )
        return jsonable_encoder(response)

    async def get_inference_data_industry_controller(
        self,
        industry: IndustryCodeEnum,
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ) -> list[StockToPredictRequestSchema]:
        response = await self.service.get_inference_data_by_industry_code(
            industry_code=industry,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
        return response

    async def get_inference_data_by_stock_tickers_controller(
        self,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ) -> list[StockToPredictRequestSchema]:
        response = await self.service.get_inference_data_by_stock_tickers(
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
        return response


def get_inference_controller() -> InferenceController:
    return InferenceController(service=get_inference_service())
