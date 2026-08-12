import logging

from fastapi import FastAPI

from backend.app.api.routes.auth import router as auth_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


app = FastAPI(
    title="Online Judge API",
    version="0.1.0",
)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
