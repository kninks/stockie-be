from typing import List

from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum


class StockInfoSchema(BaseModel):
    stock_ticker: str
    stock_name: str


class IndustryResponseSchema(BaseModel):
    industry_code: IndustryCodeEnum
    industry_name: str
    industry_description: str
    stocks: List[StockInfoSchema]
