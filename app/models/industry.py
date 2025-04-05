from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Industry(Base):
    __tablename__ = "industries"

    industry_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    stocks = relationship(
        "Stock", back_populates="industry", lazy="select", cascade="all, delete"
    )
