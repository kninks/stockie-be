from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Industry


class IndustryRepository:
    @staticmethod
    async def fetch_all(db: AsyncSession) -> list[Industry]:
        stmt = select(Industry).order_by(Industry.industry_code)
        result = await db.execute(stmt)
        industries: list[Industry] = list(result.scalars().all())
        return industries

    @staticmethod
    async def fetch_by_code(
        db: AsyncSession, industry_code: IndustryCodeEnum
    ) -> Industry:
        stmt = select(Industry).where(Industry.industry_code == industry_code)
        result = await db.execute(stmt)
        industry = result.scalar_one_or_none()
        return industry

    @staticmethod
    async def fetch_by_codes(
        db: AsyncSession, industry_codes: list[IndustryCodeEnum]
    ) -> list[Industry]:
        stmt = (
            select(Industry)
            .where(Industry.industry_code.in_(industry_codes))
            .order_by(Industry.industry_code)
        )
        result = await db.execute(stmt)
        industries: list[Industry] = list(result.scalars().all())
        return industries
