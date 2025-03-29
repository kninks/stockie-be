from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    stocks = relationship("Stock", back_populates="industry", lazy="selectin")
