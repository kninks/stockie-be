from datetime import date

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class TradingData(Base):
    __tablename__ = "trading_data"
    __table_args__ = (
        Index("ix_trading_data_lookup", "stock_ticker", "target_date"),
        UniqueConstraint("stock_ticker", "target_date", name="uq_trading_data"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_ticker: Mapped[str] = mapped_column(
        ForeignKey("stocks.ticker", ondelete="CASCADE", name="fk_trading_data_stock"),
        nullable=False,
    )
    target_date: Mapped[date] = mapped_column(Date(), nullable=False)

    close: Mapped[float] = mapped_column(Float, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    volumes: Mapped[int] = mapped_column(Integer, nullable=False)
