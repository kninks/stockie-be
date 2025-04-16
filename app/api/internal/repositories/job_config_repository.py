from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_config import JobConfig


class JobConfigRepository:
    async def fetch_by_key(self, db: AsyncSession, key: str) -> JobConfig:
        result = await db.execute(select(JobConfig).where(JobConfig.key == key))
        return result.scalars().first()

    async def fetch_by_keys(self, db: AsyncSession, keys: list[str]) -> list[JobConfig]:
        result = await db.execute(select(JobConfig).where(JobConfig.key.in_(keys)))
        return list(result.scalars().all())

    async def upsert(self, db: AsyncSession, key: str, value: str) -> JobConfig:
        existing = await self.fetch_by_key(db, key=key)
        if existing:
            stmt = (
                update(JobConfig)
                .where(JobConfig.key == key)
                .values(value=value)
                .execution_options(synchronize_session=False)
            )
            await db.execute(stmt)
        else:
            new_config = JobConfig(key=key, value=value)
            db.add(new_config)
        await db.commit()
        return await self.fetch_by_key(db, key)
