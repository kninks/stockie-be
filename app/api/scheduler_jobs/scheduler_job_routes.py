from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.scheduler_jobs.scheduler_job_controller import (
    SchedulerJobController,
    get_scheduler_job_controller,
)
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.db_session import get_db

router = APIRouter(
    prefix="/jobs",
    tags=["Scheduler Jobs"],
)


@router.post("/pull-trading-data")
async def scheduled_pull_trading_data_route(
    controller: SchedulerJobController = Depends(get_scheduler_job_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.scheduled_pull_trading_data_controller(db=db)
    return success_response()


@router.post("/trigger-infer-and-save")
async def scheduled_infer_and_save_route(
    controller: SchedulerJobController = Depends(get_scheduler_job_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.scheduled_infer_and_save_controller(db=db)
    return success_response()


@router.post("/rank-predictions")
async def scheduled_rank_predictions_route(
    controller: SchedulerJobController = Depends(get_scheduler_job_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.scheduled_rank_predictions_controller(db=db)
    return success_response()


@router.get("/evaluate-accuracy")
async def scheduled_evaluate_accuracy_route(
    controller: SchedulerJobController = Depends(get_scheduler_job_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.scheduled_evaluate_accuracy_controller(db=db)
    return success_response()


@router.delete("/cleanup")
async def scheduled_cleanup_job_route(
    controller: SchedulerJobController = Depends(get_scheduler_job_controller),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the cleanup job.
    """
    await controller.scheduled_clean_data_controller(db=db)
    return success_response()
