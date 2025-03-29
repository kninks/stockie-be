from fastapi import APIRouter, Depends

from app.core.dependencies.api_key_auth import verify_role

# from app.core.dependencies.db_session import get_db
from app.core.enums.roles_enum import RoleEnum

# from app.modules.ml_ops.controllers.inference_controller import InferenceController
# from app.modules.ml_ops.controllers.retrain_controller import RetrainController
from app.modules.ml_ops.routes import evaluation_routes

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.modules.ml_ops.schemas.inference_api_schema import InferenceRequestSchema
# from app.modules.ml_ops.schemas.retrain_api_schema import RetrainRequestSchema

router = APIRouter(
    prefix="/ml-ops",
    tags=["ML Operations"],
    dependencies=[Depends(verify_role([RoleEnum.ML_SERVER.value]))],
)

# router.include_router(retrain_routes.router, prefix="/retrain")
router.include_router(evaluation_routes.router, prefix="/evaluation")


# @router.post("/inference")
# async def route_infer_model(
#     request: InferenceRequestSchema, db: AsyncSession = Depends(get_db)
# ):
#
#     return await InferenceController.infer(request, db)
#
#
# @router.post("/retrain")
# async def route_retrain_model(request: RetrainRequestSchema):
#     """
#     Trigger model retraining by calling the ML server.
#     """
#     return await RetrainController.retrain(request)
