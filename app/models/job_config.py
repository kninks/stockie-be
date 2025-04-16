from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.common.utils.datetime_utils import get_now_bangkok_datetime
from app.models.base import Base


class JobConfig(Base):
    __tablename__ = "job_config"

    key: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_now_bangkok_datetime(),
        onupdate=get_now_bangkok_datetime(),
        server_default=func.now(),
    )
