from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.services.cleanup_data_service import (
    CleanupDataService,
    get_cleanup_data_service,
)


class CleanupDataController:
    def __init__(self, service: CleanupDataService):
        self.service = service

    async def clean_data_controller(
        self,
        db: AsyncSession,
        target_date: date,
        trading_data_days_back: int,
        predictions_days_back: int,
    ) -> None:
        await self.service.clean_data(
            db=db,
            target_date=target_date,
            trading_data_days_back=trading_data_days_back,
            predictions_days_back=predictions_days_back,
        )
        return None

    async def clean_trading_data_controller(
        self, db: AsyncSession, target_date: date, days_back: int
    ) -> None:
        await self.service.clean_trading_data(
            db=db, target_date=target_date, days_back=days_back
        )
        return None

    async def clean_predictions_controller(
        self, db: AsyncSession, target_date: date, days_back: int
    ) -> None:
        await self.service.clean_predictions(
            db=db, target_date=target_date, days_back=days_back
        )
        return None

    async def clean_top_predictions_controller(
        self, db: AsyncSession, target_date: date, days_back: int
    ) -> None:
        await self.service.clean_top_predictions(
            db=db, target_date=target_date, days_back=days_back
        )
        return None


def get_cleanup_data_controller() -> CleanupDataController:
    return CleanupDataController(service=get_cleanup_data_service())
