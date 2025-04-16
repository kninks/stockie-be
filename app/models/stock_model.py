from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.common.utils.datetime_utils import get_now_bangkok_datetime
from app.models.base import Base


class StockModel(Base):
    __tablename__ = "stock_models"
    __table_args__ = (Index("ix_stock_models_active", "stock_ticker", "is_active"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_ticker: Mapped[str] = mapped_column(
        ForeignKey("stocks.ticker", ondelete="CASCADE", name="fk_models_stock"),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    model_path: Mapped[str] = mapped_column(Text, nullable=False)
    scaler_path: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    features_used: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    additional_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_now_bangkok_datetime(),
        server_default=func.now(),
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_now_bangkok_datetime(),
        onupdate=get_now_bangkok_datetime(),
        server_default=func.now(),
    )

    stock = relationship("Stock", back_populates="models", lazy="select")
