import logging

from fastapi import FastAPI

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.dashboard import router as dashboard_router
from backend.app.api.routes.problems import router as problems_router
from backend.app.api.routes.test_cases import router as test_cases_router
from backend.app.api.routes.topics import router as topics_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


app = FastAPI(
    title="Online Judge API",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(topics_router)
app.include_router(problems_router)
app.include_router(test_cases_router)


@app.get("/health")
def health():
    return {"status": "ok"}
