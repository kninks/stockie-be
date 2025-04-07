from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.general.services.closing_price_service import (
    ClosingPriceService,
    get_closing_price_service,
)
from app.modules.general.services.prediction_service import (
    PredictionService,
    get_prediction_service,
)
from app.modules.general.services.top_prediction_service import (
    TopPredictionService,
    get_top_prediction_service,
)


class CleanupDataService:
    def __init__(
        self,
        closing_price_service: ClosingPriceService,
        prediction_service: PredictionService,
        top_prediction_service: TopPredictionService,
    ):
        self.closing_price_service = closing_price_service
        self.prediction_service = prediction_service
        self.top_prediction_service = top_prediction_service

    async def clean_data(
        self,
        db: AsyncSession,
        target_date: date,
        closing_prices_days_back: int,
        predictions_days_back: int,
    ) -> None:
        await self.clean_closing_prices(
            db=db, target_date=target_date, days_back=closing_prices_days_back
        )
        await self.clean_predictions(
            db=db, target_date=target_date, days_back=predictions_days_back
        )
        await self.clean_top_predictions(
            db=db, target_date=target_date, days_back=predictions_days_back
        )

    # TODO
    async def clean_closing_prices(
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
        closing_price_service=get_closing_price_service(),
        prediction_service=get_prediction_service(),
        top_prediction_service=get_top_prediction_service(),
    )
