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


class ClosingPrice(Base):
    __tablename__ = "closing_prices"
    __table_args__ = (
        Index("ix_closing_price_lookup", "stock_ticker", "target_date"),
        UniqueConstraint("stock_ticker", "target_date", name="uq_closing_price"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_ticker: Mapped[str] = mapped_column(
        ForeignKey("stocks.ticker", ondelete="CASCADE", name="fk_closing_price_stock"),
        nullable=False,
    )
    target_date: Mapped[date] = mapped_column(Date(), nullable=False)
    closing_price: Mapped[float] = mapped_column(Float, nullable=False)
