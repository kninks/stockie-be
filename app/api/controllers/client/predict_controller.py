from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.client.predict.predict_request_schema import PredictRequestSchema
from app.schemas.client.predict.predict_response_schema import PredictResponseSchema
from app.services.client.predict_service import PredictService


class PredictController:
    @staticmethod
    async def predict(
        request: PredictRequestSchema, db: AsyncSession
    ) -> PredictResponseSchema:
        return await PredictService().get_predictions(request, db)
