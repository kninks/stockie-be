from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.controllers.process_data_controller import (
    ProcessDataController,
    get_process_data_controller,
)
from app.api.internal.schemas.process_data_schema import (
    PullTradingDataRequestSchema,
    RankPredictionsRequestSchema,
)
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
    request: RankPredictionsRequestSchema,
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.rank_predictions_controller(request=request, db=db)
    return success_response()


@router.post("/rank-predictions")
async def rank_predictions_route(
    request: RankPredictionsRequestSchema,
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.rank_predictions_controller(request=request, db=db)
    return success_response()


@router.post("/pull-trading-data/all")
async def pull_trading_data_all_route(
    request: PullTradingDataRequestSchema,
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.pull_trading_data_controller(request=request, db=db)
    return success_response()


@router.post("/pull-trading-data")
async def pull_trading_data_route(
    request: PullTradingDataRequestSchema,
    controller: ProcessDataController = Depends(get_process_data_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.pull_trading_data_controller(request=request, db=db)
    return success_response(data=response)
