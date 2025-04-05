from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.period_enum import PeriodEnum


class PredictRequestSchema(BaseModel):
    industry: IndustryCodeEnum
    period: PeriodEnum


class TopPredictionRankSchema(BaseModel):
    rank: int
    ticker: str
    predicted_price: float
    closing_price: float


class PredictResponseSchema(BaseModel):
    ranked_stocks: list[TopPredictionRankSchema]
