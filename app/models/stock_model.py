from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from app.models.base import Base


class StockModel(Base):
    __tablename__ = "stock_models"

    id = Column(Integer, primary_key=True)
    stock_id = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE", name="fk_stock_models_stock_id"),
        nullable=False,
        index=True,
    )
    version_tag = Column(String, nullable=False)
    trained_at = Column(DateTime(timezone=True), nullable=False)
    accuracy = Column(Float)
    is_active = Column(Boolean, default=True)
    end_date = Column(DateTime(timezone=True))
    saved_path = Column(String)
    model_type = Column(String)
    model_metadata = Column(JSON)
