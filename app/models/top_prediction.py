from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class TopPrediction(Base):
    __tablename__ = "top_predictions"

    id = Column(Integer, primary_key=True)
    industry_id = Column(
        Integer,
        ForeignKey("industries.id", name="fk_top_predictions_industry_id"),
        nullable=False,
    )
    period = Column(Integer, nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(Date, nullable=False)

    top_ranks = relationship(
        "TopPredictionRank",
        back_populates="top_prediction",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_top_predictions_industry_target_period",
            "industry_id",
            "target_date",
            "period",
        ),
    )
