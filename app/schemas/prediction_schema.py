# from datetime import datetime

from pydantic import BaseModel


class PredictionQuerySchema(BaseModel):
    industry: str
    period: int
    # request_time: datetime = Field(default_factory=datetime.now())

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
