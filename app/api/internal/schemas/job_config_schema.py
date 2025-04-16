from pydantic import BaseModel

from app.core.enums.job_enum import JobConfigEnum


class ConfigUpdateRequest(BaseModel):
    key: JobConfigEnum
    value: str | int | bool
