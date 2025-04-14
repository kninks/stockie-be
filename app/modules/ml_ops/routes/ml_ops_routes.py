from fastapi import APIRouter, Depends

from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum
from app.modules.ml_ops.routes import (
    evaluation_routes,
    inference_routes,
    metadata_routes,
)

router = APIRouter(
    prefix="/ml-ops",
    dependencies=[Depends(verify_role([RoleEnum.ML_SERVER.value]))],
)

router.include_router(evaluation_routes.router)
router.include_router(inference_routes.router)
router.include_router(metadata_routes.router)
