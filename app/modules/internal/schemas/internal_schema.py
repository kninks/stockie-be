from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction


class RankPredictionsRequestSchema(BaseModel):
    industry: IndustryCodeEnum
    period: int
    target_date: date


@dataclass
class RankedPrediction:
    prediction: Prediction
    rank: int


class PullClosingPriceRequestSchema(BaseModel):
    stock_tickers: list[str]
    target_date: date
