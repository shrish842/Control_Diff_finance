from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from starlette.responses import Response

from controldiff.api.routers.health import router as health_router
from controldiff.api.routers.regulations import router as regulations_router
from controldiff.api.routers.reports import router as reports_router
from controldiff.api.routers.review import router as review_router
from controldiff.api.routers.ui import router as ui_router
from controldiff.db.base import Base
from controldiff.db.session import engine
from controldiff.logging import configure_logging
from controldiff.observability.tracing import configure_tracing

load_dotenv()
configure_logging()
configure_tracing()
Base.metadata.create_all(bind=engine)

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
STATIC_DIR = WEB_DIR / "static"

app = FastAPI(title="ControlDiff", version="0.1.0")
app.mount("/ui/static", StaticFiles(directory=str(STATIC_DIR)), name="ui-static")

app.include_router(health_router)
app.include_router(regulations_router)
app.include_router(review_router)
app.include_router(reports_router)
app.include_router(ui_router)


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "ControlDiff", "status": "ok"}


@app.get("/db/ping")
def db_ping() -> dict[str, int]:
    with engine.begin() as connection:
        connection.execute(text("SELECT 1"))
    return {"ok": 1}
