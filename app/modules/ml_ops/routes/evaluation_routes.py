from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.db_session import get_db
from app.modules.ml_ops.controllers.evaluation_controller import (
    EvaluationController,
    get_evaluation_controller,
)

router = APIRouter(
    prefix="/evaluation",
    tags=["[ml-ops] Evaluation"],
)


@router.get("/accuracy/all")
async def accuracy_route(
    controller: EvaluationController = Depends(get_evaluation_controller),
    target_date: date = Query(...),
    days_back: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate the accuracy of the model.
    """
    # Placeholder for actual implementation
    response = await controller.accuracy_all_controller(
        target_date=target_date, days_back=days_back, db=db
    )
    return success_response(data=response)


@router.get("/accuracy")
async def accuracy_all_route(
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    controller: EvaluationController = Depends(get_evaluation_controller),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate the accuracy of the model.
    """
    # Placeholder for actual implementation
    response = await controller.accuracy_controller(
        stock_tickers=stock_tickers, target_date=target_date, days_back=days_back, db=db
    )
    return success_response(data=response)
