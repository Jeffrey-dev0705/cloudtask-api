from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(pattern=r"^[a-z0-9-]+$", min_length=2, max_length=120)

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    model_config = {"from_attributes": True}
