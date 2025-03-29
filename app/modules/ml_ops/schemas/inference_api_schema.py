from datetime import datetime

from pydantic import BaseModel


class InferenceRequestSchema(BaseModel):
    stock_name: str


class InferenceResponseSchema(BaseModel):
    stock_name: str
    date: datetime
    predicted_price: float
