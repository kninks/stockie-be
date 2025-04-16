from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.public.controllers.predict_controller import (
    PredictController,
    get_predict_controller,
)
from app.api.public.schema.predict_schema import (
    GetTopPredictionResponseSchema,
)
from app.core.common.utils.response_handlers import (
    success_response,
)
from app.core.dependencies.db_session import get_db
from app.core.enums.industry_code_enum import IndustryCodeEnum

router = APIRouter(
    prefix="/predict",
)


@router.get("")
async def get_top_prediction_route(
    industry: IndustryCodeEnum = Query(...),
    period: int = Query(...),
    controller: PredictController = Depends(get_predict_controller),
    db: AsyncSession = Depends(get_db),
):
    """
    fetch the calculated result from db
    """
    response: GetTopPredictionResponseSchema = (
        await controller.get_top_prediction_controller(
            industry=industry, period=period, db=db
        )
    )
    return success_response(data=response)
