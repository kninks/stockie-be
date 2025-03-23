from fastapi import APIRouter

from app.core.common.utils.response_handlers import success_response
from app.modules.ml_ops.controllers.retrain_controller import RetrainController
from app.modules.ml_ops.schemas.retrain_api_schema import RetrainRequestSchema

router = APIRouter()


@router.post("/")
async def route_retrain_model(request: RetrainRequestSchema):
    """
    Trigger model retraining by calling the ML server.
    """
    return await success_response(data=await RetrainController.retrain(request))
