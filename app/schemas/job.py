from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    job_type: str = Field(min_length=2, max_length=80)
    priority: int = Field(default=5, ge=1, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int = Field(default=3, ge=1, le=10)

