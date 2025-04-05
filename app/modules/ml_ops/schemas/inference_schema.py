from datetime import date
from typing import Optional

from pydantic import BaseModel


class TriggerInferenceRequestSchema(BaseModel):
    stock_tickers: list[str]
    target_date: date
    days_back: int


class StockToPredictRequestSchema(BaseModel):
    stock_ticker: str
    closing_prices: list[float]
    model_id: int
    model_path: str
    scaler_path: str


class InferenceResultSchema(BaseModel):
    stock_ticker: int
    model_id: int
    target_date: date
    predicted_price: Optional[list[float]] = None
    success: bool
    error_message: Optional[str] = None


# class SaveInferenceResultRequestSchema(BaseModel):
#     inference_results: list[InferenceResultSchema]
