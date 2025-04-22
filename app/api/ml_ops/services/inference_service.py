import logging
import time
from collections import defaultdict
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dummy.dummy_service import DummyService, get_dummy_service
from app.api.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.api.general.services.stock_model_service import (
    StockModelService,
    get_stock_model_service,
)
from app.api.general.services.stock_service import StockService, get_stock_service
from app.api.general.services.trading_data_service import (
    TradingDataService,
    get_trading_data_service,
)
from app.api.ml_ops.schemas.inference_schema import (
    InferenceResultSchema,
    InferenceResultSummarySchema,
    StockToPredictRequestSchema,
)
from app.core.clients.discord_client import DiscordOperations, get_discord_operations
from app.core.clients.ml_server_operations import (
    MLServerOperations,
    get_ml_server_operations,
)
from app.core.common.exceptions.custom_exceptions import MLServerError
from app.core.common.utils.measurement import send_metric
from app.core.common.utils.validators import validate_required
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.job_enum import JobTypeEnum
from app.core.enums.measurement_enum import (
    MeasurementMetric,
    MeasurementTag,
)
from app.core.enums.trading_data_enum import TradingDataEnum
from app.models import Prediction, TradingData

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(
        self,
        stock_service: StockService,
        stock_model_service: StockModelService,
        prediction_service: PredictionService,
        trading_data_service: TradingDataService,
        dummy_service: DummyService,
        ml_operations: MLServerOperations,
        discord_operations: DiscordOperations,
    ):
        self.stock_service = stock_service
        self.stock_model_service = stock_model_service
        self.prediction_service = prediction_service
        self.trading_data_service = trading_data_service
        self.dummy_service = dummy_service
        self.ml = ml_operations
        self.discord = discord_operations

    # DONE
    async def run_and_save_inference_by_industry_code(
        self,
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        days_back: int,
        days_forward: int,
        periods: list[int],
    ) -> list[Prediction] | None:
        validate_required(industry_code, "Industry Code")
        validate_required(target_date, "Target Date")
        validate_required(days_back, "Days back")
        validate_required(days_forward, "Days forward")
        validate_required(periods, "Periods")

        stock_tickers = await self.stock_service.get_by_industry_code(
            db=db, industry_code=industry_code
        )
        stock_ticker_values = [stock.ticker for stock in stock_tickers]
        saved_predictions = await self.run_and_save_inference_by_stock_tickers(
            stock_tickers=stock_ticker_values,
            target_date=target_date,
            days_back=days_back,
            days_forward=days_forward,
            periods=periods,
            db=db,
        )
        return saved_predictions

    # DONE
    async def run_and_save_inference_by_stock_tickers(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        days_forward: int,
        periods: list[int],
    ) -> list[Prediction] | None:
        validate_required(stock_tickers, "Stock tickers")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        start = time.perf_counter()

        inference_data: list[StockToPredictRequestSchema] = (
            await self.get_inference_data_by_stock_tickers(
                stock_tickers=stock_tickers,
                target_date=target_date,
                days_back=days_back,
                db=db,
            )
        )

        inference_results: InferenceResultSummarySchema = (
            await self._make_run_inference_request_to_ml_server(
                inference_data=inference_data,
                days_forward=days_forward,
            )
        )

        success_results = inference_results.success
        failed_results = inference_results.failed

        if failed_results:
            failed_tickers = [res.stock_ticker for res in failed_results]
            await self.discord.send_discord_message(
                message=f"ML inference failed for: {failed_tickers}",
                job_name=JobTypeEnum.INFERENCE.value,
                is_critical=True,
                mention_everyone=True,
            )
            logger.error(f"ML inference failed for: {failed_tickers}")
            raise MLServerError(f"ML inference failed for: {failed_tickers}")

        saved_predictions: list[Prediction] = (
            await self._save_success_inference_results(
                target_date=target_date,
                inference_data=inference_data,
                success_results=success_results,
                periods=periods,
                db=db,
            )
        )

        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.total_predict_time,
            value=elapsed,
            tags={
                MeasurementTag.batch_size: len(stock_tickers),
                MeasurementTag.success_count: len(success_results),
                MeasurementTag.fail_count: len(failed_results),
            },
        )
        return saved_predictions

    async def run_inference_by_industry_code(
        self,
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        days_back: int,
        days_forward: int = 15,
    ) -> InferenceResultSummarySchema:
        stock_tickers = await self.stock_service.get_by_industry_code(
            db=db, industry_code=industry_code
        )
        stock_ticker_values = [stock.ticker for stock in stock_tickers]
        inference_results: InferenceResultSummarySchema = (
            await self.run_inference_by_stock_tickers(
                db=db,
                stock_tickers=stock_ticker_values,
                target_date=target_date,
                days_back=days_back,
                days_forward=days_forward,
            )
        )
        return inference_results

    async def run_inference_by_stock_tickers(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
        days_forward: int = 15,
    ) -> InferenceResultSummarySchema:
        inference_data: list[StockToPredictRequestSchema] = (
            await self.get_inference_data_by_stock_tickers(
                stock_tickers=stock_tickers,
                target_date=target_date,
                days_back=days_back,
                db=db,
            )
        )
        inference_results: InferenceResultSummarySchema = (
            await self._make_run_inference_request_to_ml_server(
                inference_data,
                days_forward=days_forward,
            )
        )

        return inference_results

    # DONE: Only for admin
    async def get_inference_data_by_industry_code(
        self,
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        target_date: date,
        days_back: int,
    ) -> list[StockToPredictRequestSchema]:
        validate_required(industry_code, "Industry Code")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        stock_tickers = await self.stock_service.get_by_industry_code(
            db=db, industry_code=industry_code
        )
        stock_ticker_values = [stock.ticker for stock in stock_tickers]
        response = await self.get_inference_data_by_stock_tickers(
            db=db,
            stock_tickers=stock_ticker_values,
            target_date=target_date,
            days_back=days_back,
        )

        return response

    # DONE
    async def get_inference_data_by_stock_tickers(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ) -> list[StockToPredictRequestSchema]:
        validate_required(stock_tickers, "Stock tickers")
        validate_required(target_date, "Target date")
        validate_required(days_back, "Days back")

        start = time.perf_counter()

        active_models = await self.stock_model_service.get_active_by_stock_tickers(
            db=db, stock_tickers=stock_tickers
        )

        trading_data_list: list[TradingData] = (
            await self.trading_data_service.get_by_stock_tickers_and_date_range(
                db=db,
                stock_tickers=stock_tickers,
                last_date=target_date,
                days_back=days_back,
            )
        )
        trading_data_map = defaultdict(
            lambda: {
                "trading_data_id": [],
                TradingDataEnum.CLOSE: [],
                TradingDataEnum.VOLUMES: [],
                TradingDataEnum.HIGH: [],
                TradingDataEnum.LOW: [],
                TradingDataEnum.OPEN: [],
            }
        )
        for trading_data in trading_data_list:
            # id of the day before the target date
            # closing prices and volumes up until the target date (includes the target date)
            trading_data_map[trading_data.stock_ticker]["trading_data_id"].append(
                trading_data.id
            )
            trading_data_map[trading_data.stock_ticker][TradingDataEnum.CLOSE].append(
                trading_data.close
            )
            trading_data_map[trading_data.stock_ticker][TradingDataEnum.VOLUMES].append(
                trading_data.volumes
            )
            trading_data_map[trading_data.stock_ticker][TradingDataEnum.HIGH].append(
                trading_data.high
            )
            trading_data_map[trading_data.stock_ticker][TradingDataEnum.LOW].append(
                trading_data.low
            )
            trading_data_map[trading_data.stock_ticker][TradingDataEnum.OPEN].append(
                trading_data.open
            )

        inference_data = [
            StockToPredictRequestSchema(
                stock_ticker=model.stock_ticker,
                trading_data_id=(
                    trading_data_map[model.stock_ticker]["trading_data_id"][-1]
                    if len(trading_data_map[model.stock_ticker]["trading_data_id"]) > 1
                    else None
                ),
                close=(
                    trading_data_map[model.stock_ticker][TradingDataEnum.CLOSE][
                        :days_back
                    ]
                    if TradingDataEnum.CLOSE in model.features_used
                    else []
                ),
                volumes=(
                    trading_data_map[model.stock_ticker][TradingDataEnum.VOLUMES][
                        :days_back
                    ]
                    if TradingDataEnum.VOLUMES in model.features_used
                    else []
                ),
                high=(
                    trading_data_map[model.stock_ticker][TradingDataEnum.HIGH][
                        :days_back
                    ]
                    if TradingDataEnum.HIGH in model.features_used
                    else []
                ),
                low=(
                    trading_data_map[model.stock_ticker][TradingDataEnum.LOW][
                        :days_back
                    ]
                    if TradingDataEnum.LOW in model.features_used
                    else []
                ),
                open=(
                    trading_data_map[model.stock_ticker][TradingDataEnum.OPEN][
                        :days_back
                    ]
                    if TradingDataEnum.OPEN in model.features_used
                    else []
                ),
                model_id=model.id,
                model_path=model.model_path,
                scaler_path=model.scaler_path,
            )
            for model in active_models
        ]

        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.get_data_time,
            value=elapsed,
            tags={
                MeasurementTag.batch_size: len(stock_tickers),
            },
        )

        return inference_data

    # DONE
    async def _make_run_inference_request_to_ml_server(
        self, inference_data: list[StockToPredictRequestSchema], days_forward: int = 15
    ) -> InferenceResultSummarySchema:
        validate_required(inference_data, "Inference data")

        start = time.perf_counter()

        raw_response = await self.ml.run_inference(
            stocks=inference_data,
            days_ahead=days_forward + 1,  # day 0 is the target date
        )
        success, failed = [], []
        for r in raw_response:
            res = InferenceResultSchema(**r)
            (success if res.success else failed).append(res)

        response = InferenceResultSummarySchema(success=success, failed=failed)
        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.ml_time,
            value=elapsed,
            tags={
                MeasurementTag.batch_size: len(inference_data),
                MeasurementTag.success_count: len(success),
                MeasurementTag.fail_count: len(failed),
            },
        )
        return response

    # DONE
    async def _save_success_inference_results(
        self,
        db: AsyncSession,
        target_date: date,
        inference_data: list[StockToPredictRequestSchema],
        success_results: list[InferenceResultSchema],
        periods: list[int],
    ) -> list[Prediction] | None:

        start = time.perf_counter()

        predictions = self._prepare_prediction_rows(
            target_date=target_date,
            inference_data=inference_data,
            success_results=success_results,
            periods=periods,
        )
        saved_predictions = await self.prediction_service.create_by_list(
            db=db, prediction_data_list=predictions
        )

        elapsed = time.perf_counter() - start
        send_metric(
            metric=MeasurementMetric.save_time,
            value=elapsed,
            tags={
                MeasurementTag.batch_size: len(predictions),
            },
        )
        return saved_predictions

    # DONE
    @staticmethod
    def _prepare_prediction_rows(
        target_date: date,
        inference_data: list[StockToPredictRequestSchema],
        success_results: list[InferenceResultSchema],
        periods: list[int],
    ) -> list[dict]:
        predictions = []
        meta_lookup = {item.stock_ticker: item for item in inference_data}

        for res in success_results:
            meta = meta_lookup.get(res.stock_ticker)
            if not meta:
                continue

            for period in periods:
                if period < len(res.predicted_price):
                    predictions.append(
                        {
                            "stock_ticker": res.stock_ticker,
                            "model_id": meta.model_id,
                            "target_date": target_date,
                            "period": period,
                            "predicted_price": res.predicted_price[period],
                            "closing_price": meta.close[-1],
                            "trading_data_id": meta.trading_data_id,
                        }
                    )

        return predictions


def get_inference_service() -> InferenceService:
    return InferenceService(
        stock_service=get_stock_service(),
        stock_model_service=get_stock_model_service(),
        prediction_service=get_prediction_service(),
        trading_data_service=get_trading_data_service(),
        dummy_service=get_dummy_service(),
        ml_operations=get_ml_server_operations(),
        discord_operations=get_discord_operations(),
    )
