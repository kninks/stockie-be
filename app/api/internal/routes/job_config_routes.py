from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.internal.controllers.job_config_controller import (
    JobConfigController,
    get_job_config_controller,
)
from app.api.internal.schemas.job_config_schema import ConfigUpdateRequest
from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.db_session import get_db
from app.core.enums.job_enum import JobConfigEnum

router = APIRouter(
    prefix="/config",
    tags=["[Internal] Job Config"],
)


@router.get("/single")
async def get_config_route(
    key: JobConfigEnum,
    db: AsyncSession = Depends(get_db),
    controller: JobConfigController = Depends(get_job_config_controller),
):
    response = await controller.get_job_config_controller(
        db=db,
        key=key,
    )
    return success_response(data=response)


@router.get("/multiple")
async def get_configs_route(
    keys: list[JobConfigEnum],
    db: AsyncSession = Depends(get_db),
    controller: JobConfigController = Depends(get_job_config_controller),
):
    response = await controller.get_job_configs_controller(
        db=db,
        keys=keys,
    )
    return success_response(data=response)


@router.patch("/single")
async def set_config_route(
    request: ConfigUpdateRequest,
    controller: JobConfigController = Depends(get_job_config_controller),
    db: AsyncSession = Depends(get_db),
):
    response = await controller.update_job_config_controller(db=db, request=request)
    return success_response(
        data=response, message="Job config updated with previous value"
    )


# @router.delete("/invalidate-cache")
# async def invalidate_cache_route(
#     key: JobConfigEnum,
#     controller: JobConfigController = Depends(get_job_config_controller),
# ):
#     await controller.invalidate_job_config_cache_controller(key=key)
#     return success_response()
#
#
# @router.delete("/invalidate-cache/all")
# async def invalidate_all_caches_route(
#     controller: JobConfigController = Depends(get_job_config_controller),
# ):
#     await controller.invalidate_all_job_config_caches_controller()
#     return success_response()
