from sqlalchemy import Column, Integer, String, Float, DateTime
from app.services.database import Base
from datetime import datetime

class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, nullable=False)
    stock_name = Column(String, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime)