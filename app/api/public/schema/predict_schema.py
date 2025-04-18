from datetime import date

from pydantic import BaseModel


class TopPredictionRankSchema(BaseModel):
    rank: int
    ticker: str
    predicted_price: float
    closing_price: float


class GetTopPredictionResponseSchema(BaseModel):
    closing_price_date: date
    predicted_price_date: date
    ranked_predictions: list[TopPredictionRankSchema]
