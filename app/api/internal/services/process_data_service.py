import logging
from datetime import date, timedelta

import yfinance as yf
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.api.general.services.stock_service import StockService, get_stock_service
from app.api.general.services.top_prediction_service import (
    TopPredictionService,
    get_top_prediction_service,
)
from app.api.general.services.trading_data_service import (
    TradingDataService,
    get_trading_data_service,
)
from app.api.internal.repositories.process_data_repository import (
    ProcessDataRepository,
)
from app.api.internal.services.job_config_service import (
    JobConfigService,
    get_job_config_service,
)
from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.datetime_utils import (
    get_last_market_open_date,
    get_n_market_days_ahead,
    get_next_market_open_date,
    is_market_closed,
)
from app.core.common.utils.validators import validate_required
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.job_enum import JobConfigEnum
from app.models import Prediction

logger = logging.getLogger(__name__)


class ProcessDataService:
    def __init__(
        self,
        process_data_repository: ProcessDataRepository,
        stock_service: StockService,
        prediction_service: PredictionService,
        top_prediction_service: TopPredictionService,
        trading_data_service: TradingDataService,
        job_config_service: JobConfigService,
    ):
        self.process_data_repository = process_data_repository
        self.stock_service = stock_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service
        self.trading_data_service = trading_data_service
        self.job_config_service = job_config_service

    async def rank_and_save_top_predictions_all(
        self,
        target_date: date,
        db: AsyncSession,
    ):
        validate_required(target_date, "target date")

        industry_codes = [item for item in IndustryCodeEnum]
        period: list[int] = await self.job_config_service.get_job_config(
            db=db, key=JobConfigEnum.SAVE_INFERENCE_PERIODS
        )

        for i in industry_codes:
            for p in period:
                await self.rank_and_save_top_prediction_one(
                    industry_code=i,
                    period=p,
                    target_date=target_date,
                    db=db,
                )

    async def rank_and_save_top_predictions(
        self,
        industry_codes: list[IndustryCodeEnum],
        periods: list[int],
        target_dates: list[date],
        db: AsyncSession,
    ) -> dict[str, list[any]]:
        validate_required(target_dates, "target date")

        results = {
            "succeeded": [],
            "failed": [],
        }

        for i in industry_codes:
            for p in periods:
                for d in target_dates:
                    try:
                        await self.rank_and_save_top_prediction_one(
                            industry_code=i,
                            period=p,
                            target_date=d,
                            db=db,
                        )
                        results["succeeded"].append((i.value, p, str(d)))
                    except Exception as e:
                        logger.error(
                            f"Ranking failed for {i.value}, period={p}, date={d}: {e}"
                        )
                        results["failed"].append((i.value, p, str(d), str(e)))

        return results

    async def rank_and_save_top_prediction_one(
        self,
        industry_code: IndustryCodeEnum,
        period: int,
        target_date: date,
        db: AsyncSession,
    ) -> None:
        validate_required(industry_code, "industry")
        validate_required(period, "period")
        validate_required(target_date, "target date")

        predictions = (
            await self.prediction_service.get_by_date_and_period_and_industry_code(
                db=db,
                target_date=target_date,
                period=period,
                industry_code=industry_code,
            )
        )

        ranked_predictions = self.rank_predictions(predictions)

        try:
            await self.process_data_repository.create_top_prediction_and_update_ranks(
                db=db,
                industry_code=industry_code,
                target_date=target_date,
                period=period,
                ranked_updates=ranked_predictions,
            )
        except Exception as e:
            logger.error(f"Failed to save top prediction: {e}")
            raise DBError("Failed to save top prediction") from e

    # DONE
    @staticmethod
    def rank_predictions(predictions: list[Prediction]) -> list[dict]:
        predictions.sort(
            key=lambda x: x.predicted_price / x.closing_price if x.closing_price else 0,
            reverse=True,
        )
        ranked_predictions = [
            {
                "prediction_id": p.id,
                "rank": i + 1,
            }
            for i, p in enumerate(predictions[:5])
        ]
        return ranked_predictions

    # DONE
    async def pull_trading_data(
        self, stock_tickers: list[str], target_date: date, db: AsyncSession
    ) -> list[str]:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")

        trading_data_list = []
        failed_tickers = []
        for stock_ticker in stock_tickers:
            try:
                ticker = stock_ticker + str(".BK")
                data = yf.download(
                    ticker,
                    start=target_date,
                    end=target_date + timedelta(days=1),
                    auto_adjust=True,
                )
                data.columns = data.columns.droplevel(1)
                if not data.empty and len(data) >= 1:
                    row = data.iloc[0]
                    trading_data_list.append(
                        {
                            "stock_ticker": stock_ticker,
                            "target_date": target_date,
                            "close": float(row["Close"]),
                            "open": float(row["Open"]),
                            "high": float(row["High"]),
                            "low": float(row["Low"]),
                            "volumes": int(row["Volume"]),
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to fetch data for {stock_ticker}: {e}")
                failed_tickers.append(stock_ticker)
                continue

        if not trading_data_list:
            logger.warning("No trading data to save.")
            return failed_tickers

        try:
            await self.trading_data_service.create_multiple(
                db=db,
                trading_data_dict_list=trading_data_list,
            )
            return failed_tickers
        except Exception as e:
            logger.error(f"Failed to pull trading data: {e}")
            raise DBError("Failed to pull trading data") from e

    async def accuracy_all(
        self,
        db: AsyncSession,
        target_date: date,
        days_back: int,
    ):
        try:
            all_stocks = await self.stock_service.get_active(db=db)
            stock_tickers = [stock.ticker for stock in all_stocks]
            await self.accuracy(
                stock_tickers=stock_tickers,
                target_date=target_date,
                days_back=days_back,
                db=db,
            )
            return
        except Exception as e:
            logger.error(f"Error in accuracy_all: {e}")
            raise e

    # TODO: find closing prices n days back -> average -> compare with the prediction
    # ** compare with what day?
    async def accuracy(
        self,
        db: AsyncSession,
        stock_tickers: list[str],
        target_date: date,
        days_back: int,
    ):
        # actual closing prices
        # all_closing_prices = await self.closing_price_service.get_closing_price_value_by_stock_tickers_and_date_range(
        #     db=db,
        #     stock_tickers=stock_tickers,
        #     target_date=target_date,
        #     days_back=days_back,
        # )
        # avg_closing_prices = [
        #     {
        #         "stock_ticker": stock_ticker,
        #         "avg_closing_price": sum(float(p) for p in closing_prices)
        #         / len(closing_prices),
        #     }
        #     for stock_ticker, closing_prices in all_closing_prices.items()
        # ]
        #
        # # predicted closing prices
        # all_predictions = (
        #     await self.prediction_service.get_by_date_and_period_and_stock_tickers(
        #         db=db, stock_tickers=stock_tickers, target_date=target_date, period=1
        #     )
        # )
        # response = await self.discord.send_discord_message(
        #     message="Accuracy Evaluation started",
        #     job_name="Accuracy Evaluation",
        # )
        # return response
        pass

    @staticmethod
    def get_market_open_date(
        target_date: date,
        n_days: int = None,
    ) -> dict[str, bool | date]:
        validate_required(target_date, "target date")
        response = {
            "target_date": target_date,
            "market_open": not is_market_closed(target_date),
            "next_market_open_date": get_next_market_open_date(target_date),
            "last_market_open_date": (
                get_last_market_open_date(target_date)
                if is_market_closed(target_date)
                else None
            ),
            "next_n_market_date": (
                get_n_market_days_ahead(start_date=target_date, n=n_days)
                if n_days
                else None
            ),
        }
        return response


def get_process_data_service() -> ProcessDataService:
    return ProcessDataService(
        process_data_repository=ProcessDataRepository(),
        stock_service=get_stock_service(),
        prediction_service=get_prediction_service(),
        top_prediction_service=get_top_prediction_service(),
        trading_data_service=get_trading_data_service(),
        job_config_service=get_job_config_service(),
    )
