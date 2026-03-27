from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from controldiff.api.deps import get_db
from controldiff.domain.dto import CreateRunRequest, RunSummary
from controldiff.domain.enums import RunStatus
from controldiff.services.regulation_service import create_regulation_run, get_run, list_runs

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


@router.post("", response_model=RunSummary)
def create_run(payload: CreateRunRequest, session: Session = Depends(get_db)) -> RunSummary:
    run = create_regulation_run(
        session=session,
        title=payload.title,
        source=payload.source,
        body_text=payload.body_text,
    )
    return RunSummary(
        run_id=run.id,
        status=RunStatus(run.status),
        regulation_title=payload.title,
        obligations_count=len(run.obligations),
        mappings_count=0,
        review_required=run.review_required,
    )


@router.get("", response_model=list[RunSummary])
def get_runs(session: Session = Depends(get_db)) -> list[RunSummary]:
    runs = list_runs(session)
    return [
        RunSummary(
            run_id=run.id,
            status=RunStatus(run.status),
            regulation_title=run.regulation.title,
            obligations_count=len(run.obligations),
            mappings_count=0,
            review_required=run.review_required,
        )
        for run in runs
    ]


@router.get("/{run_id}")
def get_run_detail(run_id: str, session: Session = Depends(get_db)) -> dict:
    run = get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "run_id": run.id,
        "status": run.status,
        "confidence": run.confidence,
        "review_required": run.review_required,
        "regulation": {
            "id": run.regulation.id,
            "title": run.regulation.title,
            "source": run.regulation.source,
            "body_text": run.regulation.body_text,
        },
        "obligations": [
            {
                "obligation_id": obligation.obligation_id,
                "text": obligation.text,
                "category": obligation.category,
                "severity": obligation.severity,
                "citations": json.loads(obligation.citations_json),
            }
            for obligation in run.obligations
        ],
    }
