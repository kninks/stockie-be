from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.roles_enum import RoleEnum
from app.modules.public.controllers.predict_controller import (
    PredictController,
)
from app.modules.public.schema.predict_schema import (
    PredictRequestSchema,
    PredictResponseSchema,
)

router = APIRouter(
    prefix="/predict",
    tags=["Top Stock"],
    dependencies=[Depends(verify_role([]))],
)


@router.get("", response_model=BaseSuccessResponse[PredictResponseSchema])
async def get_top_prediction_route(
    industry: IndustryCodeEnum = Query(...),
    period: int = Query(...),
    controller: PredictController = Depends(),
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(verify_role([RoleEnum.CLIENT.value])),
):
    """
    fetch the calculated result from db
    """
    response: PredictResponseSchema = await controller.get_top_prediction_controller(
        industry=industry, period=period, db=db
    )
    return success_response(data=response)


@router.post("/calculate", response_model=BaseSuccessResponse[None])
async def calculate_top_stock_route(
    request: PredictRequestSchema,
    controller: PredictController = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    1. fetch from db
    2. calculate the recommended stock with the highest predicted price?
    3. return the stock name and predicted price
    4. sort the rest of the stocks by predicted price
    5. for each of the rest, return the stock name and increase or decrease
    """
    await controller.calculate_and_save_top_prediction_controller(
        request=request, db=db
    )
    return success_response()
