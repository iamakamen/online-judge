import logging

from fastapi import FastAPI, Request

from backend.app.db.session import SessionLocal
from backend.app.services.authentication import (
    record_authenticated_activity as update_authenticated_activity,
)

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.ai import router as ai_router
from backend.app.api.routes.dashboard import router as dashboard_router
from backend.app.api.routes.problems import router as problems_router
from backend.app.api.routes.run import router as run_router
from backend.app.api.routes.submissions import router as submissions_router
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


@app.middleware("http")
async def record_authenticated_activity_middleware(
    request: Request,
    call_next,
):
    response = await call_next(request)
    session_id = getattr(request.state, "auth_session_id", None)

    if session_id is None or not 200 <= response.status_code < 300:
        return response

    db = SessionLocal()
    try:
        update_authenticated_activity(db, session_id)
    except Exception:
        db.rollback()
        logging.getLogger(__name__).exception(
            "Failed to record authenticated activity"
        )
    finally:
        db.close()

    return response

app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(topics_router)
app.include_router(problems_router)
app.include_router(test_cases_router)
app.include_router(run_router)
app.include_router(submissions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
