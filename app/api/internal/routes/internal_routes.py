from fastapi import APIRouter, Depends

from app.api.internal.routes import (
    cleanup_data_routes,
    job_config_routes,
    metadata_routes,
    process_data_routes,
)
from app.core.dependencies.api_key_auth import verify_role

router = APIRouter(
    prefix="/internal",
    dependencies=[Depends(verify_role([]))],
)

router.include_router(metadata_routes.router)
router.include_router(job_config_routes.router)
router.include_router(process_data_routes.router)
router.include_router(cleanup_data_routes.router)
