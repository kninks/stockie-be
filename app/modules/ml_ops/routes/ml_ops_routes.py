from fastapi import APIRouter, Depends

from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum
from app.modules.ml_ops.routes import evaluation_routes, retrain_routes

router = APIRouter(
    prefix="/ml-ops",
    tags=["ML Operations"],
    dependencies=[Depends(verify_role([RoleEnum.ML_SERVER.value]))],
)

router.include_router(retrain_routes.router, prefix="/retrain")
router.include_router(evaluation_routes.router, prefix="/evaluation")
