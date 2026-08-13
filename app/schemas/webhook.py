from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl
    event_type: str = Field(default="job.completed", pattern=r"^job\.(completed|failed)$")

