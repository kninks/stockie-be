from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.ml_ops.services.evaluation_service import (
    EvaluationService,
    get_evaluation_service,
)


class EvaluationController:
    def __init__(
        self,
        service: EvaluationService,
    ):
        self.service = service

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


def get_evaluation_controller() -> EvaluationController:
    return EvaluationController(service=get_evaluation_service())
