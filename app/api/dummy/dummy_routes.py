from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dummy.dummy_controller import DummyController, get_dummy_controller
from app.core.common.utils.response_handlers import (
    success_response,
)
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db

router = APIRouter(
    prefix="/dummy",
    tags=["Dummy"],
    dependencies=[Depends(verify_role([]))],
)


@router.post("/trading-data")
async def dummy_trading_data(
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    db: AsyncSession = Depends(get_db),
    controller: DummyController = Depends(get_dummy_controller),
):
    response = await controller.generate_dummy_trading_data_controller(
        db=db,
        stock_tickers=stock_tickers,
        end_date=target_date,
        days_back=days_back,
    )
    return success_response(data=response)


@router.post("/inference-results/all")
async def dummy_inference_results_all(
    db: AsyncSession = Depends(get_db),
    controller: DummyController = Depends(get_dummy_controller),
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    days_forward: int = Query(...),
):
    response = await controller.generate_dummy_inference_results_all_controller(
        db=db,
        target_date=target_date,
        days_back=days_back,
        days_forward=days_forward,
    )
    return success_response(response)


@router.get("/inference-results")
async def dummy_inference_results(
    db: AsyncSession = Depends(get_db),
    controller: DummyController = Depends(get_dummy_controller),
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    days_forward: int = Query(...),
):
    response = await controller.generate_dummy_inference_results_controller(
        db=db,
        stock_tickers=stock_tickers,
        target_date=target_date,
        days_back=days_back,
        days_forward=days_forward,
    )
    return success_response(response)
