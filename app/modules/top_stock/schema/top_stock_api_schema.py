from pydantic import BaseModel

from app.core.enums.industry_enum import IndustryEnum
from app.core.enums.period_enum import PeriodEnum


class TopStockRequestSchema(BaseModel):
    industry: IndustryEnum
    period: PeriodEnum


class RecommendedStockSchema(BaseModel):
    name: str
    predicted_price_upper_bound: float
    predicted_price_lower_bound: float
    is_increase: bool


class OtherStockSchema(BaseModel):
    name: str
    is_increase: bool


class TopStockResponseSchema(BaseModel):
    recommended_stock: RecommendedStockSchema
    other_stocks: list[OtherStockSchema]
