from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.public.schema.predict_schema import (
    GetTopPredictionResponseSchema,
)
from app.api.public.services.predict_service import (
    PredictService,
    get_predict_service,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum


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
        return jsonable_encoder(response)


def get_predict_controller() -> PredictController:
    return PredictController(service=get_predict_service())
