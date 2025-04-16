from sqlalchemy.ext.asyncio import AsyncSession

from app.api.scheduler_jobs.scheduler_job_service import (
    SchedulerJobService,
    get_scheduler_job_service,
)


class SchedulerJobController:
    def __init__(self, service: SchedulerJobService):
        self.service = service

    async def scheduled_pull_trading_data_controller(
        self,
        db: AsyncSession,
    ) -> None:
        await self.service.scheduled_pull_trading_data(
            db=db,
        )
        return None

    async def scheduled_infer_and_save_controller(
        self,
        db: AsyncSession,
    ) -> None:
        await self.service.scheduled_infer_and_save(
            db=db,
        )
        return None

    async def scheduled_rank_predictions_controller(
        self,
        db: AsyncSession,
    ) -> None:
        await self.service.scheduled_rank_predictions(
            db=db,
        )
        return None

    async def scheduled_evaluate_accuracy_controller(self, db: AsyncSession) -> None:
        await self.service.scheduled_evaluate_accuracy(
            db=db,
        )
        return None

    async def scheduled_clean_data_controller(
        self,
        db: AsyncSession,
    ) -> None:
        await self.service.scheduled_clean_data(
            db=db,
        )
        return None


def get_scheduler_job_controller() -> SchedulerJobController:
    return SchedulerJobController(service=get_scheduler_job_service())
