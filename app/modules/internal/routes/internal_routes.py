from fastapi import APIRouter, Depends

from app.core.dependencies.api_key_auth import verify_role
from app.modules.internal.routes import (
    cleanup_data_routes,
    job_config_routes,
    process_data_routes,
)

router = APIRouter(
    prefix="/internal",
    dependencies=[Depends(verify_role([]))],
)

router.include_router(process_data_routes.router)
router.include_router(cleanup_data_routes.router)
router.include_router(job_config_routes.router)
