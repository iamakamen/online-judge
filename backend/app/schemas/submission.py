from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    problem_id: int
    language: str
    source_code: str


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    language: str
    status: str
    verdict: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
