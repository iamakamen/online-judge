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


class SubmissionResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    display_order: int
    status: str
    execution_time_ms: int | None
    memory_used_mb: int | None
    created_at: datetime


class SubmissionDetailResponse(SubmissionResponse):
    results: list[SubmissionResultResponse]
