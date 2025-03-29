from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.top_prediction.schema.top_prediction_api_schema import (
    TopPredictionRequestSchema,
    TopPredictionResponseSchema,
)
from app.modules.top_prediction.services.top_prediction_service import (
    TopPredictionService,
)


class TopPredictionController:
    @staticmethod
    async def get_top_prediction_response(
        request: TopPredictionRequestSchema, db: AsyncSession
    ) -> TopPredictionResponseSchema:
        return await TopPredictionService().get_top_prediction(request, db)

    @staticmethod
    async def calculate_and_save_top_prediction_response(
        request: TopPredictionRequestSchema, db: AsyncSession
    ) -> None:
        return await TopPredictionService().calculate_and_save_top_prediction(
            request, db
        )
