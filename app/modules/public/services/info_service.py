import logging
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.modules.general.services.industry_service import IndustryService
from app.modules.general.services.stock_service import StockService
from app.modules.public.schema.info_schema import (
    IndustryResponseSchema,
    StockInfoSchema,
)

logger = logging.getLogger(__name__)


class InfoService:
    def __init__(
        self,
        industry_service: IndustryService = Depends(IndustryService),
        stock_service: StockService = Depends(StockService),
    ):
        self.industry_service = industry_service
        self.stock_service = stock_service

    # TODO: add more
    async def initialize_info(self, db: AsyncSession) -> List[IndustryResponseSchema]:
        response = await self.get_all_industries(db=db)
        return response

    async def get_all_industries(
        self, db: AsyncSession
    ) -> List[IndustryResponseSchema]:
        industries = await self.industry_service.get_all_industry(db=db)
        industry_dict = {
            industry.industry_code: IndustryResponseSchema(
                industry_code=IndustryCodeEnum(industry.industry_code),
                industry_name=industry.name,
                industry_description=industry.description,
                stocks=[],
            )
            for industry in industries
        }

        stocks = await self.stock_service.get_active(db=db)
        for stock in stocks:
            if stock.industry_code in industry_dict:
                industry_dict[stock.industry_code].stocks.append(
                    StockInfoSchema(stock_ticker=stock.ticker, stock_name=stock.name)
                )

        return list(industry_dict.values())
