from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    stock_id = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE", name="fk_predictions_stock_id"),
        nullable=False,
    )
    model_id = Column(
        Integer,
        ForeignKey(
            "stock_models.id", ondelete="SET NULL", name="fk_predictions_model_id"
        ),
    )
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(Date, nullable=False)
    period = Column(Integer, nullable=False)
    predicted_price = Column(Float, nullable=False)
    actual_price = Column(Float)

    stock = relationship("Stock", back_populates="predictions", lazy="select")

    __table_args__ = (
        Index(
            "ix_predictions_industry_target_period",
            "stock_id",
            "target_date",
            "period",
        ),
    )
