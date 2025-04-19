from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.controllers.cleanup_data_controller import (
    CleanupDataController,
    get_cleanup_data_controller,
)
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.db_session import get_db

router = APIRouter(
    prefix="/clean",
    tags=["[Internal] Cleanup Data"],
)


@router.delete("/all")
async def clean_data_route(
    db: AsyncSession = Depends(get_db),
    controller: CleanupDataController = Depends(get_cleanup_data_controller),
    target_date: date = Query(...),
    trading_days_back: int = Query(),
    predictions_days_back: int = Query(),
):
    await controller.clean_data_controller(
        db=db,
        target_date=target_date,
        trading_data_days_back=trading_days_back,
        predictions_days_back=predictions_days_back,
    )
    return success_response()


@router.delete("/trading_data")
async def clean_trading_data_route(
    db: AsyncSession = Depends(get_db),
    controller: CleanupDataController = Depends(get_cleanup_data_controller),
    target_date: date = Query(...),
    days_back: int = Query(),
):
    await controller.clean_trading_data_controller(
        target_date=target_date, days_back=days_back, db=db
    )
    return success_response()


@router.delete("/predictions")
async def clean_predictions_route(
    db: AsyncSession = Depends(get_db),
    controller: CleanupDataController = Depends(get_cleanup_data_controller),
    target_date: date = Query(...),
    days_back: int = Query(),
):
    await controller.clean_predictions_controller(
        target_date=target_date, days_back=days_back, db=db
    )
    return success_response()


@router.delete("/top-predictions")
async def clean_top_predictions_route(
    db: AsyncSession = Depends(get_db),
    controller: CleanupDataController = Depends(get_cleanup_data_controller),
    target_date: date = Query(...),
    days_back: int = Query(30, ge=1),
):
    await controller.clean_top_predictions_controller(
        target_date=target_date, days_back=days_back, db=db
    )
    return success_response()
