from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI

from controldiff.api.routers.health import router as health_router
from controldiff.api.routers.regulations import router as regulations_router

from controldiff.db.session import init_db
from controldiff.logging import configure_logging

load_dotenv()
configure_logging()
init_db()

app = FastAPI(title="ControlDiff", version="0.1.0")
app.include_router(health_router)
app.include_router(regulations_router)

@app.get("/")
def root() -> dict[str, str]:
    return {"name": "ControlDiff", "status": "ok"}
