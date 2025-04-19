from fastapi import APIRouter, Depends

from app.api.ml_ops.routes import (
    inference_routes,
)
from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum

router = APIRouter(
    prefix="/ml-ops",
    dependencies=[Depends(verify_role([RoleEnum.ML_SERVER.value]))],
)

router.include_router(inference_routes.router)
