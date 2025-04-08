import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients.discord_client import DiscordOperations, get_discord_operations
from app.core.clients.redis_client import redis_client
from app.core.common.utils.validators import (
    validate_entity_exists,
    validate_exact_length,
    validate_required,
)
from app.core.enums.job_enum import JobConfigEnum
from app.modules.internal.repositories.job_config_repository import JobConfigRepository

REDIS_TTL_SECONDS = 60 * 5

logger = logging.getLogger(__name__)


class JobConfigService:
    def __init__(
        self,
        job_config_repository: JobConfigRepository,
        discord: DiscordOperations,
        redis_client_instance=redis_client,
    ):
        self.job_config_repository = job_config_repository
        self.discord = discord
        self.redis_client = redis_client_instance

    async def get_job_config(
        self, db: AsyncSession, key: JobConfigEnum
    ) -> str | int | bool:
        validate_required(key, "key")
        cache_key = f"config:{key}"
        cached = await self.redis_client.get(cache_key)

        if cached is not None:
            return self.smart_cast(cached)

        config = await self.job_config_repository.fetch_by_key(db=db, key=key)
        validate_entity_exists(config, "config")
        return self.smart_cast(config.value)

    async def get_job_configs(
        self, db: AsyncSession, keys: list[JobConfigEnum]
    ) -> list[dict[JobConfigEnum, str | int | bool]]:
        validate_required(keys, "keys")

        if len(keys) == 1:
            config = await self.job_config_repository.fetch_by_key(db=db, key=keys[0])
            configs_dict = (
                [{JobConfigEnum(config.key): self.smart_cast(config.value)}]
                if config
                else []
            )
        else:
            configs = await self.job_config_repository.fetch_by_keys(db=db, keys=keys)
            configs_dict = [
                {JobConfigEnum(config.key): self.smart_cast(config.value)}
                for config in configs
            ]

        validate_entity_exists(configs_dict, "configs_dict")
        validate_exact_length(configs_dict, len(keys), "configs_dict")
        return configs_dict

    async def set_job_config(
        self, db: AsyncSession, key: JobConfigEnum, value: str
    ) -> str | int | bool:
        validate_required(key, "key")
        validate_required(value, "value")
        result = await self.job_config_repository.upsert(db, key, value)
        validate_entity_exists(result, "result")

        await self.discord.send_discord_message(
            message=f"🔧 Job config `{key}` updated to `{value}`",
            job_name="Config Update",
            mention_everyone=True,
        )

        await self.invalidate_job_config_cache(key)
        return result.value

    async def invalidate_job_config_cache(self, key: JobConfigEnum):
        await self.redis_client.delete(f"config:{key}")
        pass

    async def invalidate_all_job_config_caches(self):
        keys = [key async for key in redis_client.scan_iter(match="config:*")]
        if keys:
            await self.redis_client.delete(*keys)
            logger.info(f"✅ Invalidated {len(keys)} config cache keys.")
        else:
            logger.info("ℹ️ No config cache keys found to invalidate.")
        pass

    @staticmethod
    def smart_cast(value: str) -> str | int | bool:
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        if value.isdigit():
            return int(value)
        return value


def get_job_config_service() -> JobConfigService:
    return JobConfigService(
        job_config_repository=JobConfigRepository(), discord=get_discord_operations()
    )
