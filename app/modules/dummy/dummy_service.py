import random
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.validators import (
    normalize_stock_tickers,
    validate_required,
)
from app.modules.general.services.feature_service import (
    FeatureService,
    get_feature_service,
)
from app.modules.general.services.stock_model_service import (
    StockModelService,
    get_stock_model_service,
)
from app.modules.general.services.stock_service import StockService, get_stock_service
from app.modules.ml_ops.schemas.inference_schema import InferenceResultSchema


class DummyService:
    def __init__(
        self,
        stock_service: StockService,
        stock_model_service: StockModelService,
        feature_service: FeatureService,
    ):
        self.stock_service = stock_service
        self.stock_model_service = stock_model_service
        self.feature_service = feature_service

    # async def generate_dummy_inference_results_all(
    #     self,
    #     db: AsyncSession,
    #     target_date: date,
    #     days_back: int,
    #     days_forward: int,
    # ) -> list[InferenceResultSchema]:
    #     all_stock_tickers = await self.stock_service.get_active_ticker_values(db=db)
    #     return await self.generate_dummy_inference_results(
    #         db=db,
    #         stock_tickers=all_stock_tickers,
    #         target_date=target_date,
    #         days_back=days_back,
    #         days_forward=days_forward,
    #     )
    #
    # async def generate_dummy_inference_results(
    #     self,
    #     db: AsyncSession,
    #     stock_tickers: list[str],
    #     target_date: date,
    #     days_back: int,
    #     days_forward: int,
    # ) -> list[InferenceResultSchema]:
    #     validate_required(stock_tickers, "stock_tickers")
    #     validate_required(target_date, "target_date")
    #     validate_required(days_back, "days_back")
    #     validate_required(days_forward, "days_forward")
    #     stock_tickers = normalize_stock_tickers(stock_tickers)
    #
    #     all_models = await self.stock_model_service.get_active(db=db)
    #     all_features = (
    #         await self.feature_service.get_by_stock_tickers_and_date_range(
    #             stock_tickers=stock_tickers,
    #             target_date=target_date,
    #             days_back=days_back,
    #             db=db,
    #         )
    #     )
    #
    #     features_lookup = { feature.stock_ticker: feature for feature in all_features }
    #
    #     inference_results = []
    #
    #     for model in all_models:
    #         ticker = model.stock_ticker
    #         model_id = model.id
    #         feature_item = features_lookup.get(ticker)
    #
    #         actual_closing_price = feature_item.close[-2]
    #         # closing_price_id = actual_closing_price_item.id
    #         predicted_prices = [
    #             actual_closing_price + random.uniform(-5, 5)
    #             for i in range(days_forward + 1)
    #         ]
    #
    #         # print("model_id", model_id, "for ticker", ticker)
    #         # print(
    #         #     "target date",
    #         #     target_date,
    #         #     ": id",
    #         #     closing_price_id,
    #         #     "=",
    #         #     actual_closing_price,
    #         # )
    #         # print("actual_closing_prices_list")
    #         # print([a.closing_price for a in actual_closing_prices_list[:days_back]])
    #         # print("predicted_prices")
    #         # print(predicted_prices)
    #
    #         inference_result = InferenceResultSchema(
    #             stock_ticker=ticker,
    #             model_id=model_id,
    #             target_date=target_date,
    #             predicted_price=predicted_prices,
    #             success=True,
    #             error_message=None,
    #         )
    #         inference_results.append(inference_result)
    #
    #     return inference_results


def get_dummy_service() -> DummyService:
    return DummyService(
        stock_service=get_stock_service(),
        stock_model_service=get_stock_model_service(),
        feature_service=get_feature_service(),
    )
