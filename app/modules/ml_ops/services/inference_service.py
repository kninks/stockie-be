import logging
from datetime import date
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import MLServerError
from app.core.common.utils.validators import validate_required
from app.modules.general.services.closing_price_service import ClosingPriceService
from app.modules.general.services.prediction_service import PredictionService
from app.modules.general.services.stock_model_service import StockModelService
from app.modules.ml_ops.clients.ml_server_operations import MLServerOperations
from app.modules.ml_ops.schemas.inference_schema import (
    InferenceResultSchema,
    StockToPredictRequestSchema,
)

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(
        self,
        stock_model_service: StockModelService = Depends(StockModelService),
        prediction_service: PredictionService = Depends(PredictionService),
        closing_price_service: ClosingPriceService = Depends(ClosingPriceService),
        ml_operations: MLServerOperations = Depends(MLServerOperations),
    ):
        self.stock_model_service = stock_model_service
        self.prediction_service = prediction_service
        self.closing_price_service = closing_price_service
        self.ml_operations = ml_operations

    # TODO: add error handling + improve performance + implement retry for the failed stock tickers
    async def run_and_save_inference_by_stock_tickers(
        self,
        stock_tickers: List[str],
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ) -> None:
        """
        Run inference with only the stock tickers as the input and save the results to the database.
        """
        validate_required(stock_tickers, "Stock tickers")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")
        inference_data = await self.get_inference_data_by_stock_tickers(
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )

        inference_results: List[InferenceResultSchema] = (
            await self._make_run_inference_request_to_ml_server(
                inference_data=inference_data
            )
        )

        success_results = [i for i in inference_results if i.success]
        failed_results = [i for i in inference_results if not i.success]
        if failed_results:
            failed_tickers = [res.stock_ticker for res in failed_results]
            raise MLServerError(f"ML inference failed for: {failed_tickers}")

        await self._save_success_inference_results(
            inference_data=inference_data,
            success_results=success_results,
            db=db,
        )

        return

    # TODO: Add error handling
    async def run_inference_by_stock_tickers(
        self,
        stock_tickers: List[str],
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ) -> List[InferenceResultSchema]:
        """
        Run inference with only the stock tickers as the input and return the results without saving to the database.
        This is just for debugging purpose.
        """
        inference_data = await self.get_inference_data_by_stock_tickers(
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            db=db,
        )
        inference_results: List[InferenceResultSchema] = (
            await self._make_run_inference_request_to_ml_server(inference_data)
        )
        return inference_results

    # TODO (done): check accuracy of the logic
    async def get_inference_data_by_stock_tickers(
        self,
        stock_tickers: List[str],
        target_date: date,
        days_back: int,
        db: AsyncSession,
    ) -> List[StockToPredictRequestSchema]:
        """
        Get the inference data by stock tickers.
        """
        validate_required(stock_tickers, "Stock tickers")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        active_models = await self.stock_model_service.get_active_by_stock_tickers(
            db=db, stock_tickers=stock_tickers
        )
        closing_prices_map = await self.closing_price_service.get_closing_price_value_by_stock_tickers_and_date_range(
            db=db,
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
        )

        inference_data = [
            StockToPredictRequestSchema(
                stock_ticker=model.stock_ticker,
                closing_prices=closing_prices_map.get(model.stock_ticker),
                model_id=model.id,
                model_path=model.model_path,
                scaler_path=model.scaler_path,
            )
            for model in active_models
        ]

        return inference_data

    # TODO: error handling
    async def _make_run_inference_request_to_ml_server(
        self, inference_data: List[StockToPredictRequestSchema]
    ) -> List[InferenceResultSchema]:
        """
        Make a request to the ML server to run inference.
        """
        validate_required(inference_data, "Inference data")
        response = await self.ml_operations.run_inference(stocks=inference_data)
        return response

    # TODO: error handling
    async def _save_success_inference_results(
        self,
        inference_data: List[StockToPredictRequestSchema],
        success_results: List[InferenceResultSchema],
        db: AsyncSession,
    ) -> None:
        predictions = self._prepare_prediction_rows(inference_data, success_results)
        await self.prediction_service.create_by_list(
            db=db, prediction_data_list=predictions
        )
        return

    # TODO (done): closing price (already nullable in the schema)
    @staticmethod
    def _prepare_prediction_rows(
        inference_data: List[StockToPredictRequestSchema],
        success_results: List[InferenceResultSchema],
        periods: List[int] = [1, 3, 5, 10, 15],
    ) -> List[dict]:
        predictions = []

        for res in success_results:
            meta = next(
                (
                    item
                    for item in inference_data
                    if item.stock_ticker == res.stock_ticker
                ),
                None,
            )
            if not meta:
                continue  # Optionally log warning

            for period in periods:
                if period >= len(meta.closing_prices):
                    continue

                predictions.append(
                    {
                        "stock_ticker": res.stock_ticker,
                        "model_id": res.model_id,
                        "target_date": res.target_date,
                        "period": period,
                        "predicted_price": res.predicted_price[period],
                        "closing_price": meta.closing_prices[period],
                        "closing_price_id": None,
                    }
                )

        return predictions
