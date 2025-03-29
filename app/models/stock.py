from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    industry_id = Column(
        Integer,
        ForeignKey("industries.id", name="fk_stocks_industry_id"),
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    industry = relationship("Industry", back_populates="stocks", lazy="select")
    predictions = relationship("Prediction", back_populates="stock", lazy="select")
