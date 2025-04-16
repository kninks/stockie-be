import random
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.general.services.stock_model_service import (
    StockModelService,
    get_stock_model_service,
)
from app.api.general.services.stock_service import StockService, get_stock_service
from app.api.general.services.trading_data_service import (
    TradingDataService,
    get_trading_data_service,
)
from app.api.ml_ops.schemas.inference_schema import InferenceResultSchema
from app.core.common.utils.validators import (
    normalize_stock_tickers,
    validate_required,
)
from app.models import TradingData


class DummyService:
    def __init__(
        self,
        stock_service: StockService,
        stock_model_service: StockModelService,
        trading_data_service: TradingDataService,
    ):
        self.stock_service = stock_service
        self.stock_model_service = stock_model_service
        self.trading_data_service = trading_data_service

    @staticmethod
    async def generate_dummy_trading_data(
        db: AsyncSession,
        stock_tickers: list[str],
        end_date: date,
        days_back: int,
    ) -> list[TradingData]:
        data_to_insert = []
        for ticker in stock_tickers:
            price = random.uniform(120, 200)
            for i in range(days_back):
                target_date = end_date - timedelta(days=days_back - i - 1)
                closing_price = price + random.uniform(-5, 5)
                opening_price = closing_price + random.uniform(-2, 2)
                high = max(opening_price, closing_price) + random.uniform(0, 3)
                low = min(opening_price, closing_price) - random.uniform(0, 3)
                volumes = random.randint(1000, 10000)
                price = round(max(price, 80), 2)
                data_to_insert.append(
                    TradingData(
                        stock_ticker=ticker,
                        target_date=target_date,
                        close=closing_price,
                        open=opening_price,
                        high=high,
                        low=low,
                        volumes=volumes,
                    )
                )
        db.add_all(data_to_insert)
        await db.commit()

        return data_to_insert

    async def generate_dummy_inference_results_all(
        self,
        db: AsyncSession,
        target_date: date,
        days_back: int,
        days_forward: int,
    ) -> list[InferenceResultSchema]:
        all_stock_tickers = await self.stock_service.get_active_ticker_values(db=db)
        return await self.generate_dummy_inference_results(
            db=db,
            stock_tickers=all_stock_tickers,
            target_date=target_date,
            days_back=days_back,
            days_forward=days_forward,
        )

    async def generate_dummy_inference_results(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        days_forward: int,
    ) -> list[InferenceResultSchema]:
        validate_required(stock_tickers, "stock_tickers")
        validate_required(target_date, "target_date")
        validate_required(days_back, "days_back")
        validate_required(days_forward, "days_forward")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        all_models = await self.stock_model_service.get_active_by_stock_tickers(
            db=db, stock_tickers=stock_tickers
        )
        all_trading_data_all_stocks = (
            await self.trading_data_service.get_by_stock_tickers_and_date_range(
                stock_tickers=stock_tickers,
                last_date=target_date,
                days_back=days_back,
                db=db,
            )
        )

        trading_data_lookup = defaultdict(list[TradingData])
        for trading_data in all_trading_data_all_stocks:
            trading_data_lookup[trading_data.stock_ticker].append(trading_data)

        inference_results = []
        for model in all_models:
            ticker = model.stock_ticker
            trading_data_item_list: list[TradingData] = trading_data_lookup.get(ticker)

            target_date_yesterday_trading_data_item = trading_data_item_list[-2]
            yesterday_actual_closing_price = (
                target_date_yesterday_trading_data_item.close
            )

            # trading_data_id = target_date_yesterday_trading_data_item.id
            predicted_prices = [
                yesterday_actual_closing_price + random.uniform(-5, 5)
                for i in range(days_forward + 1)
            ]

            # print("model_id", model_id, "for ticker", ticker)
            # print(
            #     "target date",
            #     target_date,
            #     ": id",
            #     trading_data_id,
            #     "=",
            #     yesterday_actual_closing_price,
            # )
            # print("trading_data_item_list")
            # print([a.close for a in trading_data_item_list[:days_back]])
            # print("predicted_prices")
            # print(predicted_prices)

            inference_result = InferenceResultSchema(
                stock_ticker=ticker,
                predicted_price=predicted_prices,
                success=True,
                error_message=None,
            )
            inference_results.append(inference_result)

        return inference_results


def get_dummy_service() -> DummyService:
    return DummyService(
        stock_service=get_stock_service(),
        stock_model_service=get_stock_model_service(),
        trading_data_service=get_trading_data_service(),
    )
