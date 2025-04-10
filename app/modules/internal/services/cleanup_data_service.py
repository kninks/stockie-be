from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.modules.general.services.top_prediction_service import (
    TopPredictionService,
    get_top_prediction_service,
)
from app.modules.general.services.trading_data_service import (
    TradingDataService,
    get_trading_data_service,
)


class CleanupDataService:
    def __init__(
        self,
        trading_data_service: TradingDataService,
        prediction_service: PredictionService,
        top_prediction_service: TopPredictionService,
    ):
        self.trading_data_service = trading_data_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service

    async def clean_data(
        self,
        db: AsyncSession,
        target_date: date,
        trading_data_days_back: int,
        predictions_days_back: int,
    ) -> None:
        await self.clean_trading_data(
            db=db, target_date=target_date, days_back=trading_data_days_back
        )
        await self.clean_predictions(
            db=db, target_date=target_date, days_back=predictions_days_back
        )
        await self.clean_top_predictions(
            db=db, target_date=target_date, days_back=predictions_days_back
        )

    # TODO
    async def clean_trading_data(
        self, db: AsyncSession, target_date: date, days_back: int
    ) -> None:
        pass

    # TODO
    async def clean_predictions(
        self, db: AsyncSession, target_date: date, days_back: int
    ) -> None:
        pass

    # TODO
    async def clean_top_predictions(
        self, db: AsyncSession, target_date: date, days_back: int
    ) -> None:
        pass


def get_cleanup_data_service() -> CleanupDataService:
    return CleanupDataService(
        trading_data_service=get_trading_data_service(),
        prediction_service=get_prediction_service(),
        top_prediction_service=get_top_prediction_service(),
    )
