import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import (
    validate_entity_exists,
    validate_enum_input,
    validate_exact_length,
    validate_required,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Industry
from app.modules.general.repositories.industry_repository import IndustryRepository

logger = logging.getLogger(__name__)


class IndustryService:
    def __init__(
        self,
        industry_repository: IndustryRepository,
    ):
        self.industry_repo = industry_repository

    async def get_all_industry(self, db: AsyncSession) -> List[Industry]:
        try:
            industries = await self.industry_repo.fetch_all(db=db)
        except Exception as e:
            logger.error(f"Failed to fetch all industries: {e}")
            raise DBError("Failed to fetch all industries") from e

        validate_entity_exists(industries, "Industries")
        validate_exact_length(industries, 8, "industries")
        return industries

    async def get_by_code(
        self, db: AsyncSession, industry_code: IndustryCodeEnum
    ) -> Industry:
        validate_required(industry_code, "industry code")
        validate_enum_input(industry_code, IndustryCodeEnum, "industry code")

        try:
            industry = await self.industry_repo.fetch_by_code(
                db=db, industry_code=industry_code
            )
        except Exception as e:
            logger.error(f"Failed to fetch industry with code '{industry_code}': {e}")
            raise DBError("Failed to fetch industry") from e

        validate_entity_exists(industry, f"Industry code '{industry_code}'")
        return industry

    async def get_by_codes(
        self, db: AsyncSession, industry_codes: List[IndustryCodeEnum]
    ) -> List[Industry]:
        validate_required(industry_codes, "industry codes")
        validate_enum_input(industry_codes, IndustryCodeEnum, "industry codes")

        try:
            if len(industry_codes) == 1:
                industry = await self.industry_repo.fetch_by_code(
                    db=db, industry_code=industry_codes[0]
                )
                industries = [industry] if industry else []
            else:
                industries = await self.industry_repo.fetch_by_codes(
                    db=db, industry_codes=industry_codes
                )
        except Exception as e:
            logger.error(f"Failed to fetch industries for codes {industry_codes}: {e}")
            raise DBError("Failed to fetch industries") from e

        validate_entity_exists(industries, f"Industries for codes {industry_codes}")
        validate_exact_length(industries, len(industry_codes), "industries")
        return industries


def get_industry_service() -> IndustryService:
    return IndustryService(industry_repository=IndustryRepository())
