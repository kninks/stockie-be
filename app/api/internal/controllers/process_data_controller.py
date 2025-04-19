from datetime import date
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.schemas.process_data_schema import (
    PullTradingDataRequestSchema,
    RankPredictionsRequestSchema,
)
from app.api.internal.services.process_data_service import (
    ProcessDataService,
    get_process_data_service,
)


class ProcessDataController:
    def __init__(self, service: ProcessDataService):
        self.service = service

    async def rank_and_save_top_predictions_all_controller(
        self, target_date: date, db: AsyncSession
    ) -> None:
        response = await self.service.rank_and_save_top_predictions_all(
            target_date=target_date,
            db=db,
        )
        return response

    async def rank_and_save_top_predictions_controller(
        self, request: RankPredictionsRequestSchema, db: AsyncSession
    ) -> dict[str, list[any]]:
        response: dict[str, list[any]] = (
            await self.service.rank_and_save_top_predictions(
                industry_codes=request.industries,
                periods=request.periods,
                target_dates=request.target_dates,
                db=db,
            )
        )
        return response

    async def pull_trading_data_controller(
        self, request: PullTradingDataRequestSchema, db: AsyncSession
    ) -> list[str]:
        response = await self.service.pull_trading_data(
            stock_tickers=request.stock_tickers,
            target_date=request.target_date,
            db=db,
        )
        return response

    async def accuracy_all_controller(
        self,
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ):
        response = await self.service.accuracy_all(
            target_date=target_date, days_back=days_back, db=db
        )
        return response

    async def accuracy_controller(
        self,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ):
        response = await self.service.accuracy(
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
        return response

    def get_market_open_date_controller(
        self, target_date: date, next_n_market_days: Optional[int]
    ) -> dict[str, bool | date]:
        response: dict[str, bool | date] = self.service.get_market_open_date(
            target_date=target_date, n_days=next_n_market_days
        )
        return jsonable_encoder(response)


def get_process_data_controller() -> ProcessDataController:
    return ProcessDataController(service=get_process_data_service())
