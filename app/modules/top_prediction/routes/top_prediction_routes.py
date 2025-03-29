from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.period_enum import PeriodEnum
from app.core.enums.roles_enum import RoleEnum
from app.modules.top_prediction.controllers.top_prediction_controller import (
    TopPredictionController,
)
from app.modules.top_prediction.schema.top_prediction_api_schema import (
    TopPredictionRequestSchema,
    TopPredictionResponseSchema,
)

router = APIRouter(
    prefix="/top-prediction",
    tags=["Top Stock"],
)


@router.get("")
async def route_get_top_prediction(
    industry: IndustryCodeEnum = Query(...),
    period: PeriodEnum = Query(...),
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(verify_role([RoleEnum.CLIENT.value])),
):
    """
    fetch the calculated result from db
    """
    request: TopPredictionRequestSchema = TopPredictionRequestSchema(
        industry=industry, period=period
    )
    response: TopPredictionResponseSchema = (
        await TopPredictionController.get_top_prediction_response(request, db)
    )
    return await success_response(data=response)


@router.post("/calculate")
async def route_calculate_top_stock(
    request: TopPredictionRequestSchema,
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(verify_role([RoleEnum.CLIENT.value])),
):
    """
    1. fetch from db
    2. calculate the recommended stock with the highest predicted price?
    3. return the stock name and predicted price
    4. sort the rest of the stocks by predicted price
    5. for each of the rest, return the stock name and increase or decrease
    """
    await TopPredictionController.calculate_and_save_top_prediction_response(
        request, db
    )
    return await success_response()
