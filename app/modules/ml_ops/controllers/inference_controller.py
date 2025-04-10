from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ml_ops.schemas.inference_schema import (
    InferenceResultSchema,
    StockToPredictRequestSchema,
    TriggerAllInferenceRequestSchema,
    TriggerInferenceRequestSchema,
)
from app.modules.ml_ops.services.inference_service import (
    InferenceService,
    get_inference_service,
)


class InferenceController:
    def __init__(self, service: InferenceService):
        self.service = service

    async def infer_and_save_all(
        self,
        request: TriggerAllInferenceRequestSchema,
        db: AsyncSession,
    ) -> None:
        response = await self.service.run_and_save_inference_all(
            target_date=request.target_date,
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

    async def infer_only(
        self,
        request: TriggerInferenceRequestSchema,
        db: AsyncSession,
    ) -> list[InferenceResultSchema]:
        response = await self.service.run_inference_by_stock_tickers(
            stock_tickers=request.stock_tickers,
            target_date=request.target_date,
            days_back=request.days_back,
            db=db,
        )
        return response

    async def get_all_inference_data_controller(
        self,
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ) -> list[StockToPredictRequestSchema]:
        response = await self.service.get_all_inference_data(
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

    # async def save_only(
    #     self,
    #     request: SaveInferenceResultRequestSchema,
    #     db: AsyncSession,
    # ) -> None:
    #     response = await self.service._save_success_inference_results(
    #         inference_results=request.inference_results, db=db
    #     )
    #     return response


def get_inference_controller() -> InferenceController:
    return InferenceController(service=get_inference_service())
