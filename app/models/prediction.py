from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (
        Index("ix_predictions_lookup", "stock_ticker", "target_date", "period"),
        UniqueConstraint(
            "stock_ticker", "model_id", "target_date", "period", name="uq_prediction"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("stock_models.id", ondelete="CASCADE", name="fk_predictions_model"),
        nullable=False,
    )

    stock_ticker: Mapped[str] = mapped_column(
        ForeignKey("stocks.ticker", ondelete="CASCADE", name="fk_predictions_stock"),
        nullable=False,
    )
    target_date: Mapped[date] = mapped_column(Date(), nullable=False)
    period: Mapped[int] = mapped_column(Integer, nullable=False)

    closing_price: Mapped[float] = mapped_column(Float, nullable=True)
    feature_id: Mapped[int] = mapped_column(
        ForeignKey(
            "features.id",
            ondelete="CASCADE",
            name="fk_predictions_feature",
        ),
        nullable=True,
    )
    predicted_price: Mapped[float] = mapped_column(Float, nullable=False)

    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("top_predictions.id", name="fk_predictions_top"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(),
        server_default=func.now(),
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(),
        onupdate=datetime.now(),
        server_default=func.now(),
    )

    stock = relationship("Stock", back_populates="predictions", lazy="select")
