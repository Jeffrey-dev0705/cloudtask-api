from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    job_type: str = Field(min_length=2, max_length=80)
    priority: int = Field(default=5, ge=1, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int = Field(default=3, ge=1, le=10)

class JobResponse(BaseModel):
    id: UUID
    job_type: str
    status: str
    priority: int
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error_message: str | None = None
    attempts: int
    max_attempts: int
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    model_config = {"from_attributes": True}
