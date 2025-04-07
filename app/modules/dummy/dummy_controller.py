from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dummy.dummy_service import DummyService, get_dummy_service


class DummyController:
    def __init__(self, dummy_service: DummyService):
        self.dummy_service = dummy_service

    async def generate_dummy_inference_results_all_controller(
        self,
        db: AsyncSession,
        target_date: date,
        days_back: int,
        days_forward: int,
    ):
        response = await self.dummy_service.generate_dummy_inference_results_all(
            db=db,
            target_date=target_date,
            days_back=days_back,
            days_forward=days_forward,
        )
        return [res.model_dump(mode="json") for res in response]

    async def generate_dummy_inference_results_controller(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        days_forward: int,
    ):
        response = await self.dummy_service.generate_dummy_inference_results(
            db=db,
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            days_forward=days_forward,
        )
        return [res.model_dump(mode="json") for res in response]


def get_dummy_controller() -> DummyController:
    return DummyController(dummy_service=get_dummy_service())
