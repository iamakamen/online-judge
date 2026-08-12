from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TopicCreate(BaseModel):
    name: str
    slug: str
    display_order: int


class TopicUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    display_order: int | None = None


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    display_order: int
    created_at: datetime
    updated_at: datetime
