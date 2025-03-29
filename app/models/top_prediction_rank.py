from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class TopPredictionRank(Base):
    __tablename__ = "top_prediction_ranks"

    id = Column(Integer, primary_key=True)
    top_prediction_id = Column(
        Integer,
        ForeignKey("top_predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction_id = Column(
        Integer, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False
    )
    rank = Column(Integer, nullable=False)

    top_prediction = relationship(
        "TopPrediction", back_populates="top_ranks", lazy="select"
    )
    prediction = relationship("Prediction", lazy="joined")
