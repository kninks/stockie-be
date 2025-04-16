import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.general.services.industry_service import (
    IndustryService,
    get_industry_service,
)
from app.api.general.services.stock_service import StockService, get_stock_service
from app.api.public.schema.info_schema import (
    IndustryResponseSchema,
    InitialInfoResponseSchema,
    PeriodResponseSchema,
    StockInfoSchema,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum

logger = logging.getLogger(__name__)


class InfoService:
    def __init__(
        self,
        industry_service: IndustryService,
        stock_service: StockService,
    ):
        self.industry_service = industry_service
        self.stock_service = stock_service

    async def initialize_info(self, db: AsyncSession) -> InitialInfoResponseSchema:
        period_values = [1, 5, 10, 15]
        all_periods: list[PeriodResponseSchema] = [
            PeriodResponseSchema(value=val, label=f"{val} day{'s' if val > 1 else ''}")
            for val in period_values
        ]

        all_industries = await self._get_all_industries(db=db)

        response = InitialInfoResponseSchema(
            all_periods=all_periods,
            all_industries=all_industries,
        )
        return response

    async def _get_all_industries(
        self, db: AsyncSession
    ) -> List[IndustryResponseSchema]:
        industries = await self.industry_service.get_all_industry(db=db)
        industry_dict = {
            industry.industry_code: IndustryResponseSchema(
                industry_code=IndustryCodeEnum(industry.industry_code),
                industry_name_en=industry.name_en,
                industry_name_th=industry.name_th,
                industry_description_en=industry.description_en,
                industry_description_th=industry.description_th,
                stocks_info=[],
            )
            for industry in industries
        }

        stocks = await self.stock_service.get_active(db=db)
        for stock in stocks:
            if stock.industry_code in industry_dict:
                industry_dict[stock.industry_code].stocks_info.append(
                    StockInfoSchema(stock_ticker=stock.ticker, stock_name=stock.name)
                )

        return list(industry_dict.values())


def get_info_service() -> InfoService:
    return InfoService(
        industry_service=get_industry_service(),
        stock_service=get_stock_service(),
    )
