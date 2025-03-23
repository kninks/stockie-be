from app.modules.ml_ops.schemas.retrain_api_schema import RetrainRequestSchema
from app.modules.ml_ops.services.retrain_service import RetrainService


class RetrainController:
    @staticmethod
    async def retrain(request: RetrainRequestSchema):
        return await RetrainService.trigger_retrain(request)
