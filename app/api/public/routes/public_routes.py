from fastapi import APIRouter, Depends

from app.api.public.routes import info_routes, predict_routes
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.enums.roles_enum import RoleEnum

router = APIRouter(
    tags=["Public"],
    dependencies=[Depends(verify_role([RoleEnum.CLIENT.value]))],
)


@router.get("/health")
async def health_check(
    user_role: str = Depends(verify_role([RoleEnum.ML_SERVER.value])),
):
    return success_response(message="Backend is healthy", data={"role": user_role})


router.include_router(info_routes.router)
router.include_router(predict_routes.router)
