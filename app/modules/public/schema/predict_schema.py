from pydantic import BaseModel


class TopPredictionRankSchema(BaseModel):
    rank: int
    ticker: str
    predicted_price: float
    closing_price: float


class GetTopPredictionResponseSchema(BaseModel):
    ranked_predictions: list[TopPredictionRankSchema]
