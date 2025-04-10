from datetime import date

from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum


class RankPredictionsRequestSchema(BaseModel):
    industry: IndustryCodeEnum
    period: int
    target_date: date


class PullTradingDataRequestSchema(BaseModel):
    stock_tickers: list[str]
    target_date: date
