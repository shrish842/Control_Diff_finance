from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from controldiff.api.deps import get_db
from controldiff.services.regulation_service import get_run
from controldiff.services.report_service import build_report

router = APIRouter(prefix="/api/v1/runs", tags=["reports"])


@router.get("/{run_id}/report")
def get_report(run_id: str, session: Session = Depends(get_db)) -> dict:
    run = get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return build_report(session, run)
