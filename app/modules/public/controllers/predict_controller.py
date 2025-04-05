from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.modules.public.schema.predict_schema import (
    PredictRequestSchema,
    PredictResponseSchema,
)
from app.modules.public.services.predict_service import (
    PredictService,
)


class PredictController:
    def __init__(self, service: PredictService = Depends(PredictService)):
        self.service = service

    async def get_top_prediction_controller(
        self,
        industry: IndustryCodeEnum,
        period: int,
        db: AsyncSession,
    ) -> PredictResponseSchema:
        response = await self.service.get_top_prediction(
            industry=industry, period=period, db=db
        )
        return response

    async def calculate_and_save_top_prediction_controller(
        self,
        request: PredictRequestSchema,
        db: AsyncSession,
    ) -> None:
        response = await self.service.calculate_and_save_top_prediction(
            request=request, db=db
        )
        return response
