from datetime import date
from typing import Optional

from pydantic import BaseModel


class TriggerAllInferenceRequestSchema(BaseModel):
    target_date: date
    days_back: int = 60
    days_forward: int = 15
    periods: list[int] = [1, 5, 10, 15]


class TriggerInferenceRequestSchema(BaseModel):
    stock_tickers: list[str]
    target_date: date
    days_back: int = 60
    days_forward: int = 15
    periods: list[int] = [1, 5, 10, 15]


class StockToPredictRequestSchema(BaseModel):
    stock_ticker: str
    trading_data_id: Optional[int] = None
    close: list[float]
    volumes: Optional[list[int]] = []
    model_id: int
    model_path: str
    scaler_path: str


class InferenceResultSchema(BaseModel):
    stock_ticker: str
    target_date: date
    predicted_price: Optional[list[float]] = None
    success: bool
    error_message: Optional[str] = None


# class SaveInferenceResultRequestSchema(BaseModel):
#     inference_results: list[InferenceResultSchema]
