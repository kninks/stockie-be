import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients.discord_client import DiscordOperations, get_discord_operations
from app.modules.general.services.closing_price_service import (
    ClosingPriceService,
    get_closing_price_service,
)
from app.modules.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.modules.general.services.stock_service import StockService, get_stock_service

logger = logging.getLogger(__name__)


class EvaluationService:
    def __init__(
        self,
        discord_operations: DiscordOperations,
        stock_service: StockService,
        closing_price_service: ClosingPriceService,
        prediction_service: PredictionService,
    ):
        self.discord = discord_operations
        self.stock_service = stock_service
        self.closing_price_service = closing_price_service
        self.prediction_service = prediction_service

    # TODO
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
        except Exception as e:
            logger.error(f"Error in accuracy_all: {e}")
            # await self.discord.send_discord_message(
            #     message=f"Error in accuracy_all: {e}",
            #     job_name="Accuracy Evaluation (all)",
            #     is_critical=True,
            #     mention_everyone=True,
            # )
            raise e
        response = await self.discord.send_discord_message(
            "Accuracy Evaluation for all stocks started",
            job_name="Accuracy Evaluation (all)",
        )
        return response

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


def get_evaluation_service() -> EvaluationService:
    return EvaluationService(
        discord_operations=get_discord_operations(),
        stock_service=get_stock_service(),
        closing_price_service=get_closing_price_service(),
        prediction_service=get_prediction_service(),
    )
