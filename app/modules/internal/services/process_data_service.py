import logging
import yfinance as yf
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import validate_required
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction
from app.modules.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.modules.general.services.stock_service import StockService, get_stock_service
from app.modules.general.services.top_prediction_service import (
    TopPredictionService,
    get_top_prediction_service,
)
from app.modules.general.services.trading_data_service import (
    TradingDataService,
    get_trading_data_service,
)
from app.modules.internal.repositories.process_data_repository import (
    ProcessDataRepository,
)

logger = logging.getLogger(__name__)


class ProcessDataService:
    def __init__(
        self,
        process_data_repository: ProcessDataRepository,
        stock_service: StockService,
        prediction_service: PredictionService,
        top_prediction_service: TopPredictionService,
        trading_data_service: TradingDataService,
    ):
        self.process_data_repository = process_data_repository
        self.stock_service = stock_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service
        self.trading_data_service = trading_data_service

    async def rank_and_save_top_predictions_all(
        self,
        period: int,
        target_date: date,
        db: AsyncSession,
    ):
        validate_required(period, "period")
        validate_required(target_date, "target date")

        industry_codes = [item for item in IndustryCodeEnum]
        for industry_code in industry_codes:
            await self.rank_and_save_top_prediction(
                industry_code=industry_code,
                period=period,
                target_date=target_date,
                db=db,
            )

    async def rank_and_save_top_prediction(
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
        print(ranked_predictions)

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

    # TODO
    async def pull_trading_data_all(self, target_date: date, db: AsyncSession) -> None:
        validate_required(target_date, "target date")
        stock_tickers = await self.stock_service.get_active_ticker_values(db=db)
        await self.pull_trading_data(
            stock_tickers=stock_tickers, target_date=target_date, db=db
        )

    # DONE
    async def pull_trading_data(
        self, stock_tickers: list[str], target_date: date, db: AsyncSession
    ) -> None:
        validate_required(stock_tickers, "stock tickers")
        validate_required(target_date, "target date")

        trading_data_list = []
        for stock_ticker in stock_tickers:
            try:
                ticker = stock_ticker + str(".BK")
                print(stock_ticker)
                data = yf.download(ticker, start=target_date, end=target_date+ timedelta(days=1), auto_adjust=True)
                data.columns = data.columns.droplevel(1)
                print(data)
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
                continue

        if not trading_data_list:
            logger.warning("No trading data to save.")
            return []

        try:
            await self.trading_data_service.create_multiple(
                db=db,
                trading_data_dict_list=trading_data_list,
            )
            return [d["stock_ticker"] for d in trading_data_list]
        except Exception as e:
            logger.error(f"Failed to pull closing prices: {e}")
            raise DBError("Failed to pull closing prices") from e


def get_process_data_service() -> ProcessDataService:
    return ProcessDataService(
        process_data_repository=ProcessDataRepository(),
        stock_service=get_stock_service(),
        prediction_service=get_prediction_service(),
        top_prediction_service=get_top_prediction_service(),
        trading_data_service=get_trading_data_service(),
    )
