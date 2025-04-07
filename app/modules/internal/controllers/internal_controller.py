from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.internal.schemas.internal_schema import RankPredictionsRequestSchema
from app.modules.internal.services.internal_service import (
    InternalService,
    get_internal_service,
)


class InternalController:
    def __init__(self, service: InternalService):
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

    async def pull_closing_prices_controller(
        self, request: RankPredictionsRequestSchema, db: AsyncSession
    ) -> None:
        response = await self.service.pull_closing_prices(
            stock_tickers=request.stock_tickers, target_date=request.target_date, db=db
        )
        return response


def get_internal_controller() -> InternalController:
    return InternalController(service=get_internal_service())
