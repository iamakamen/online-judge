from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt

from backend.app.models.problem import Difficulty
from backend.app.schemas.test_case import PublicTestCaseResponse


class ProblemCreate(BaseModel):
    topic_id: int
    title: str
    slug: str
    statement: str
    difficulty: Difficulty
    tags: list[str]
    starter_code: dict[str, str]
    time_limit_ms: PositiveInt
    memory_limit_mb: PositiveInt


class ProblemUpdate(BaseModel):
    topic_id: int | None = None
    title: str | None = None
    slug: str | None = None
    statement: str | None = None
    difficulty: Difficulty | None = None
    tags: list[str] | None = None
    starter_code: dict[str, str] | None = None
    time_limit_ms: PositiveInt | None = None
    memory_limit_mb: PositiveInt | None = None


class ProblemListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    created_by_user_id: int | None
    title: str
    slug: str
    difficulty: Difficulty
    tags: list[str]


class ProblemDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    created_by_user_id: int | None
    title: str
    slug: str
    statement: str
    difficulty: Difficulty
    tags: list[str]
    starter_code: dict[str, str]
    time_limit_ms: PositiveInt
    memory_limit_mb: PositiveInt
    created_at: datetime
    updated_at: datetime
    test_cases: list[PublicTestCaseResponse]
