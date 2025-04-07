from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.job_enum import JobConfigEnum
from app.modules.internal.schemas.job_config_schema import ConfigUpdateRequest
from app.modules.internal.services.job_config_service import (
    JobConfigService,
    get_job_config_service,
)


class JobConfigController:
    def __init__(self, service: JobConfigService):
        self.service = service

    async def get_job_config_controller(
        self,
        key: JobConfigEnum,
        db: AsyncSession,
    ) -> str | int | bool:
        return await self.service.get_job_config(db=db, key=key)

    async def get_job_configs_controller(
        self,
        keys: list[JobConfigEnum],
        db: AsyncSession,
    ) -> list[dict[JobConfigEnum, str | int | bool]]:
        response = await self.service.get_job_configs(db=db, keys=keys)
        return response

    async def update_job_config_controller(
        self,
        request: ConfigUpdateRequest,
        db: AsyncSession,
    ):
        return await self.service.set_job_config(
            db=db, key=request.key, value=request.value
        )

    async def invalidate_job_config_cache_controller(self, key: JobConfigEnum) -> None:
        await self.service.invalidate_job_config_cache(key=key)
        return None

    async def invalidate_all_job_config_caches_controller(self) -> None:
        await self.service.invalidate_all_job_config_caches()
        return None


def get_job_config_controller() -> JobConfigController:
    return JobConfigController(service=get_job_config_service())
