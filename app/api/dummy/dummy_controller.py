from datetime import date

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dummy.dummy_service import DummyService, get_dummy_service


class DummyController:
    def __init__(self, service: DummyService):
        self.dummy_service = service

    async def generate_dummy_trading_data_controller(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        end_date: date,
        days_back: int,
    ):
        response = await self.dummy_service.generate_dummy_trading_data(
            db=db,
            stock_tickers=stock_tickers,
            end_date=end_date,
            days_back=days_back,
        )
        serialized_data = jsonable_encoder(response)
        return serialized_data

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
    return DummyController(service=get_dummy_service())
