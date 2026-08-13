from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl
    event_type: str = Field(default="job.completed", pattern=r"^job\.(completed|failed)$")

class WebhookResponse(BaseModel):
    id: UUID
    url: str
    event_type: str
    active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class WebhookCreatedResponse(WebhookResponse):
    secret: str
