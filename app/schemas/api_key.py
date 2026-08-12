from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    expires_at: datetime | None = None

class ApiKeyCreatedResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    secret: str
    expires_at: datetime | None = None

class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    active: bool
    created_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    model_config = {"from_attributes": True}
