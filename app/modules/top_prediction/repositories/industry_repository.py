from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import ResourceNotFoundError
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Industry


class IndustryRepository:
    @staticmethod
    async def get_by_code(db: AsyncSession, code: IndustryCodeEnum) -> Industry:
        stmt = select(Industry).where(Industry.code == code)
        result = await db.execute(stmt)
        industry = result.scalar_one_or_none()
        if not industry:
            raise ResourceNotFoundError(f"Industry code '{code}' not found.")
        return industry


industry_repository = IndustryRepository()
