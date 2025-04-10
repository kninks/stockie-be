import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients.discord_client import DiscordOperations, get_discord_operations
from app.core.clients.ml_server_operations import (
    MLServerOperations,
    get_ml_server_operations,
)
from app.core.common.exceptions.custom_exceptions import MLServerError
from app.core.common.utils.validators import validate_required
from app.core.enums.job_enum import JobTypeEnum
from app.models import Feature, Prediction
from app.modules.dummy.dummy_service import DummyService, get_dummy_service
from app.modules.general.services.feature_service import (
    FeatureService,
    get_feature_service,
)
from app.modules.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.modules.general.services.stock_model_service import (
    StockModelService,
    get_stock_model_service,
)
from app.modules.general.services.stock_service import StockService, get_stock_service
from app.modules.ml_ops.schemas.inference_schema import (
    InferenceResultSchema,
    StockToPredictRequestSchema,
)

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(
        self,
        stock_service: StockService,
        stock_model_service: StockModelService,
        prediction_service: PredictionService,
        feature_service: FeatureService,
        dummy_service: DummyService,
        ml_operations: MLServerOperations,
        discord_operations: DiscordOperations,
    ):
        self.stock_service = stock_service
        self.stock_model_service = stock_model_service
        self.prediction_service = prediction_service
        self.feature_service = feature_service
        self.dummy_service = dummy_service
        self.ml = ml_operations
        self.discord = discord_operations

    # DONE
    async def run_and_save_inference_all(
        self,
        db: AsyncSession,
        target_date: date,
        days_back: int,
        days_forward: int,
    ) -> list[Prediction] | None:
        all_stocks = await self.stock_service.get_active(db=db)
        stock_tickers = [stock.ticker for stock in all_stocks]
        saved_predictions = await self.run_and_save_inference_by_stock_tickers(
            stock_tickers=stock_tickers,
            target_date=target_date,
            days_back=days_back,
            days_forward=days_forward,
            db=db,
        )
        return saved_predictions

    # FIXME:
    #  add error handling
    #  improve performance
    #  notify on failed stocks : Done
    async def run_and_save_inference_by_stock_tickers(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        days_forward: int,
    ) -> list[Prediction] | None:
        """
        Run inference with only the stock tickers as the input and save the results to the database.
        """
        validate_required(stock_tickers, "Stock tickers")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        inference_data: list[StockToPredictRequestSchema] = (
            await self.get_inference_data_by_stock_tickers(
                stock_tickers=stock_tickers,
                target_date=target_date,
                days_back=days_back,
                db=db,
            )
        )
        pass

        # inference_results: list[InferenceResultSchema] = (
        #     await self._make_run_inference_request_to_ml_server(
        #     await self._make_run_inference_request_to_ml_server(
        #         inference_data=inference_data
        #     )
        # )

        # inference_results: list[InferenceResultSchema] = (
        #     await self.dummy_service.generate_dummy_inference_results(
        #         db=db,
        #         stock_tickers=stock_tickers,
        #         target_date=target_date,
        #         days_back=days_back,
        #         days_forward=days_forward,
        #     )
        # )
        #
        # success_results = [i for i in inference_results if i.success]
        # failed_results = [i for i in inference_results if not i.success]
        # if failed_results:
        #     failed_tickers = [res.stock_ticker for res in failed_results]
        #     await self.discord.send_discord_message(
        #         message=f"ML inference failed for: {failed_tickers}",
        #         job_name=JobTypeEnum.INFERENCE.value,
        #         is_critical=True,
        #         mention_everyone=True,
        #     )
        #     logger.error(f"ML inference failed for: {failed_tickers}")
        #     raise MLServerError(f"ML inference failed for: {failed_tickers}")
        #
        # saved_predictions = await self._save_success_inference_results(
        #     inference_data=inference_data,
        #     success_results=success_results,
        #     db=db,
        # )
        #
        # return saved_predictions

    # FIXME: Add error handling
    async def run_inference_by_stock_tickers(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[InferenceResultSchema]:
        """
        Run inference with only the stock tickers as the input and return the results without saving to the database.
        This is just for debugging purpose.
        """
        inference_data: list[StockToPredictRequestSchema] = (
            await self.get_inference_data_by_stock_tickers(
                stock_tickers=stock_tickers,
                target_date=target_date,
                days_back=days_back,
                db=db,
            )
        )
        inference_results: list[InferenceResultSchema] = (
            await self._make_run_inference_request_to_ml_server(inference_data)
        )
        return inference_results

    # DONE
    async def get_all_inference_data(
        self,
        db: AsyncSession,
        target_date: date,
        days_back: int,
    ) -> list[StockToPredictRequestSchema]:
        """
        Get the inference data by stock tickers.
        """
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        active_stocks: list[str] = await self.stock_service.get_active_ticker_values(
            db=db
        )
        inference_data = await self.get_inference_data_by_stock_tickers(
            db=db,
            stock_tickers=active_stocks,
            target_date=target_date,
            days_back=days_back,
        )

        return inference_data

    # DONE
    async def get_inference_data_by_stock_tickers(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[StockToPredictRequestSchema]:
        """
        Get the inference data by stock tickers.
        """
        validate_required(stock_tickers, "Stock tickers")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        active_models = await self.stock_model_service.get_active_by_stock_tickers(
            db=db, stock_tickers=stock_tickers
        )
        features_list: list[Feature] = (
            await self.feature_service.get_by_stock_tickers_and_date_range(
                db=db,
                stock_tickers=stock_tickers,
                target_date=target_date,
                days_back=days_back,
            )
        )
        features_map = {
            feature.stock_ticker: {
                "close": feature.close,
                "volumes": feature.volumes,
            }
            for feature in features_list
        }

        inference_data = [
            StockToPredictRequestSchema(
                stock_ticker=model.stock_ticker,
                close=features_map.get(model.stock_ticker).get("close")[:days_back],
                volumes=features_map.get(model.stock_ticker).get("volume")[:days_back],
                model_id=model.id,
                model_path=model.model_path,
                scaler_path=model.scaler_path,
            )
            for model in active_models
        ]

        return inference_data

    # DONE
    async def _make_run_inference_request_to_ml_server(
        self, inference_data: list[StockToPredictRequestSchema]
    ) -> list[InferenceResultSchema]:
        """
        Make a request to the ML server to run inference.
        """
        validate_required(inference_data, "Inference data")
        response = await self.ml.run_inference(stocks=inference_data)
        return response

    # DONE
    async def _save_success_inference_results(
        self,
        db: AsyncSession,
        inference_data: list[StockToPredictRequestSchema],
        success_results: list[InferenceResultSchema],
    ) -> list[Prediction]:
        predictions = self._prepare_prediction_rows(inference_data, success_results)
        saved_predictions = await self.prediction_service.create_by_list(
            db=db, prediction_data_list=predictions
        )
        return saved_predictions

    # DONE: closing price id (already nullable in the schema)
    @staticmethod
    def _prepare_prediction_rows(
        inference_data: list[StockToPredictRequestSchema],
        success_results: list[InferenceResultSchema],
    ) -> list[dict]:
        periods = [1, 5, 10, 15]
        predictions = []
        meta_lookup = {item.stock_ticker: item for item in inference_data}

        for res in success_results:
            meta = meta_lookup.get(res.stock_ticker)
            if not meta:
                continue

            for period in periods:
                if period < len(res.predicted_price):  # ← same as your original logic
                    predictions.append(
                        {
                            "stock_ticker": res.stock_ticker,
                            "model_id": res.model_id,
                            "target_date": res.target_date,
                            "period": period,
                            "predicted_price": res.predicted_price[period],
                            "closing_price": meta.close[-1],
                            "feature_id": None,  #
                        }
                    )

        return predictions


def get_inference_service() -> InferenceService:
    return InferenceService(
        stock_service=get_stock_service(),
        stock_model_service=get_stock_model_service(),
        prediction_service=get_prediction_service(),
        feature_service=get_feature_service(),
        dummy_service=get_dummy_service(),
        ml_operations=get_ml_server_operations(),
        discord_operations=get_discord_operations(),
    )
