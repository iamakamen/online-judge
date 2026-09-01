from pydantic import BaseModel


class AcceptedSolutionsResponse(BaseModel):
    solutions: dict[str, str | None]
