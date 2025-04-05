from enum import Enum
from typing import Optional
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel


# Dummy enum and models for isolated test purposes
class IndustryCodeEnum(str, Enum):
    TECH = "TECH"
    AGRI = "AGRI"


class Industry(BaseModel):
    industry_code: str
    name: str
    description: Optional[str] = None


class DBError(Exception):
    pass


class IndustryService:
    def __init__(self, industry_repository):
        self.industry_repo = industry_repository

    async def get_all(self, db):
        try:
            industries = await self.industry_repo.fetch_all(db=db)
        except Exception as e:
            raise DBError("Failed to fetch all industries") from e
        if not industries:
            raise DBError("Industries not found")
        return industries

    async def get_by_code(self, db, industry_code: IndustryCodeEnum):
        try:
            industry = await self.industry_repo.fetch_by_code(
                db=db, industry_code=industry_code
            )
        except Exception as e:
            raise DBError("Failed to fetch industry") from e
        if not industry:
            raise DBError("Industry not found")
        return industry

    async def get_by_codes(self, db, industry_codes):
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
            raise DBError("Failed to fetch industries") from e
        if not industries:
            raise DBError("Industries not found")
        return industries


# Now create test cases
@pytest.fixture
def mock_industry_repo():
    return AsyncMock()


@pytest.fixture
def industry_service(mock_industry_repo):
    return IndustryService(industry_repository=mock_industry_repo)


@pytest.mark.asyncio
async def test_get_all_industries_success(industry_service, mock_industry_repo):
    mock_industry_repo.fetch_all.return_value = [
        Industry(industry_code="AGRI", name="Agriculture")
    ]
    result = await industry_service.get_all(db="fake_db")
    assert len(result) == 1
    assert result[0].industry_code == "AGRI"


@pytest.mark.asyncio
async def test_get_by_code_success(industry_service, mock_industry_repo):
    mock_industry_repo.fetch_by_code.return_value = Industry(
        industry_code="TECH", name="Tech"
    )
    result = await industry_service.get_by_code(
        db="fake_db", industry_code=IndustryCodeEnum.TECH
    )
    assert result.industry_code == "TECH"


@pytest.mark.asyncio
async def test_get_by_codes_multiple(industry_service, mock_industry_repo):
    mock_industry_repo.fetch_by_codes.return_value = [
        Industry(industry_code="TECH", name="Tech"),
        Industry(industry_code="AGRI", name="Agri"),
    ]
    result = await industry_service.get_by_codes(
        db="fake_db", industry_codes=[IndustryCodeEnum.TECH, IndustryCodeEnum.AGRI]
    )
    assert len(result) == 2
    assert {i.industry_code for i in result} == {"TECH", "AGRI"}
