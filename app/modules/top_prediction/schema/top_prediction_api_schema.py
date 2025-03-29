from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.period_enum import PeriodEnum


class TopPredictionRequestSchema(BaseModel):
    industry: IndustryCodeEnum
    period: PeriodEnum

    class Config:
        use_enum_values = True


class TopPredictionRankSchema(BaseModel):
    rank: int
    ticker: str
    predicted_price: float
    actual_price: float


class TopPredictionResponseSchema(BaseModel):
    ranked_stocks: list[TopPredictionRankSchema]
