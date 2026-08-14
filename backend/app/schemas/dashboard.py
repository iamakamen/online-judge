from pydantic import BaseModel


class DashboardResponse(BaseModel):
    first_name: str
    solved_count: int
    day_streak: int
    global_rank: str
