from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.modules.public.schema.predict_schema import (
    GetTopPredictionResponseSchema,
)
from app.modules.public.services.predict_service import (
    PredictService,
    get_predict_service,
)


class PredictController:
    def __init__(self, service: PredictService = Depends(PredictService)):
        self.service = service

    async def get_top_prediction_controller(
        self,
        industry: IndustryCodeEnum,
        period: int,
        db: AsyncSession,
    ) -> GetTopPredictionResponseSchema:
        response = await self.service.get_top_prediction(
            industry=industry, period=period, db=db
        )
        return response


def get_predict_controller() -> PredictController:
    return PredictController(service=get_predict_service())
