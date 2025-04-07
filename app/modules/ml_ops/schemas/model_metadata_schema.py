from typing import Optional

from pydantic import BaseModel


class ModelMetadataResponseSchema(BaseModel):
    model_id: int
    stock_ticker: str
    version: str
    accuracy: float
    model_path: str
    scaler_path: str
    additional_data: Optional[dict] = None


class SaveModelMetadataRequestSchema(BaseModel):
    stock_ticker: str
    version: str
    accuracy: float
    model_path: str
    scaler_path: str
    additional_data: Optional[dict] = None
