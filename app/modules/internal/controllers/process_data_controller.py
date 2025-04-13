from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.internal.schemas.process_data_schema import (
    PullTradingDataRequestSchema,
    RankPredictionsRequestSchema,
)
from app.modules.internal.services.process_data_service import (
    ProcessDataService,
    get_process_data_service,
)


class ProcessDataController:
    def __init__(self, service: ProcessDataService):
        self.service = service

    async def rank_predictions_controller(
        self, request: RankPredictionsRequestSchema, db: AsyncSession
    ) -> None:
        response = await self.service.rank_and_save_top_prediction(
            industry_code=request.industry,
            period=request.period,
            target_date=request.target_date,
            db=db,
        )
        return response

    async def pull_trading_data_controller(
        self, request: PullTradingDataRequestSchema, db: AsyncSession
    ) -> None:
        response = await self.service.pull_trading_data(
            stock_tickers=request.stock_tickers, target_date=request.target_date, db=db
        )
        return response


def get_process_data_controller() -> ProcessDataController:
    return ProcessDataController(service=get_process_data_service())
