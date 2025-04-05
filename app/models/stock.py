from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Stock(Base):
    __tablename__ = "stocks"
    __table_args__ = (Index("ix_stocks_industry_active", "industry_code", "is_active"),)

    ticker: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    industry_code: Mapped[str] = mapped_column(
        ForeignKey(
            "industries.industry_code",
            ondelete="CASCADE",
            name="fk_stocks_industry_code",
        ),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default='true'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(),
        server_default=func.now(),
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(),
        onupdate=datetime.now(),
        server_default=func.now(),
    )

    industry = relationship("Industry", back_populates="stocks", lazy="select")
    models = relationship(
        "StockModel", back_populates="stock", lazy="select", cascade="all, delete"
    )
    predictions = relationship(
        "Prediction", back_populates="stock", lazy="select", cascade="all, delete"
    )
