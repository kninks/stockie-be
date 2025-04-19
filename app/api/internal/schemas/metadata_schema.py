from typing import Optional

from pydantic import BaseModel

from app.core.enums.trading_data_enum import TradingDataEnum


class ModelMetadataResponseSchema(BaseModel):
    model_id: int
    stock_ticker: str
    version: str
    accuracy: float
    model_path: str
    scaler_path: str
    features_used: list[TradingDataEnum]
    additional_data: Optional[dict] = None


class SaveModelMetadataRequestSchema(BaseModel):
    stock_ticker: str
    version: str
    accuracy: float
    model_path: str
    scaler_path: str
    features_used: list[TradingDataEnum]
    additional_data: Optional[dict] = None
