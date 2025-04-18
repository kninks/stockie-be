from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum


class PeriodResponseSchema(BaseModel):
    value: int
    label: str


class StockInfoSchema(BaseModel):
    stock_ticker: str
    stock_name: str


class IndustryResponseSchema(BaseModel):
    industry_code: IndustryCodeEnum
    industry_name_en: str
    industry_name_th: str
    industry_description_en: str
    industry_description_th: str
    stocks_info: list[StockInfoSchema]


class InitialInfoResponseSchema(BaseModel):
    all_periods: list[PeriodResponseSchema]
    all_industries: list[IndustryResponseSchema]
