from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TopPrediction(Base):
    __tablename__ = "top_predictions"
    __table_args__ = (
        Index("ix_top_predictions_lookup", "industry_code", "target_date", "period"),
        UniqueConstraint(
            "industry_code", "target_date", "period", name="uq_top_prediction"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    industry_code: Mapped[str] = mapped_column(
        ForeignKey("industries.industry_code", name="fk_top_prediction_industry"),
        nullable=False,
    )
    target_date: Mapped[date] = mapped_column(Date(), nullable=False)
    period: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(),
        server_default=func.now(),
    )
