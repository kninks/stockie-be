from datetime import date

from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum


class RankPredictionsRequestSchema(BaseModel):
    industries: list[IndustryCodeEnum]
    periods: list[int]
    target_dates: list[date]


class PullTradingDataRequestSchema(BaseModel):
    stock_tickers: list[str]
    target_dates: date
