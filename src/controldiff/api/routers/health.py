from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from controldiff.api.deps import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/liveness")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/readiness")
def readiness(session: Session = Depends(get_db)) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ready"}
