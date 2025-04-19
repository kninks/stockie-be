from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.controllers.process_data_controller import (
    ProcessDataController,
    get_process_data_controller,
)
from app.api.internal.schemas.process_data_schema import (
    PullTradingDataRequestSchema,
    RankPredictionsRequestSchema,
)
from app.core.common.utils.datetime_utils import get_today_bangkok_date
from app.core.common.utils.response_handlers import (
    success_response,
)
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db

router = APIRouter(
    prefix="/process",
    tags=["[Internal] Process Data"],
    dependencies=[Depends(verify_role([]))],
)


@router.post("/rank-predictions/all")
async def rank_predictions_all_route(
    target_date: date = Query(default=get_today_bangkok_date()),
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.rank_and_save_top_predictions_all_controller(
        target_date=target_date, db=db
    )
    return success_response()


@router.post("/rank-predictions")
async def rank_predictions_route(
    request: RankPredictionsRequestSchema,
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.rank_and_save_top_predictions_controller(
        request=request, db=db
    )
    return success_response(data=response)


@router.post("/pull-trading-data")
async def pull_trading_data_route(
    request: PullTradingDataRequestSchema,
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.pull_trading_data_controller(request=request, db=db)
    return success_response(data=response)


@router.get("/evaluate-accuracy/all")
async def accuracy_all_route(
    target_date: date = Query(default=get_today_bangkok_date()),
    days_back: int = Query(default=15),
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.accuracy_all_controller(
        target_date=target_date, days_back=days_back, db=db
    )
    return success_response(data=response)


@router.get("/evaluate-accuracy")
async def accuracy_route(
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(default=get_today_bangkok_date()),
    days_back: int = Query(default=15),
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.accuracy_controller(
        stock_tickers=stock_tickers, target_date=target_date, days_back=days_back, db=db
    )
    return success_response(data=response)


@router.get("/market-open-date")
def market_open_date_route(
    target_date: date = Query(get_today_bangkok_date()),
    next_n_market_days: Optional[int] = Query(default=None),
    controller: ProcessDataController = Depends(get_process_data_controller),
):
    response: dict[str, bool | date] = controller.get_market_open_date_controller(
        target_date=target_date, next_n_market_days=next_n_market_days
    )
    return success_response(data=response)
