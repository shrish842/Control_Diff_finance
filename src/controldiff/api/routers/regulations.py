from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from controldiff.api.deps import get_db
from controldiff.domain.dto import RunSummary
from controldiff.services.regulation_service import create_regulation_run, get_run, list_runs
from controldiff.services.report_service import build_report

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


class CreateRunRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    source: str = Field(min_length=3, max_length=255)
    body_text: str = Field(min_length=20)


@router.post("", response_model=RunSummary)
def create_run(payload: CreateRunRequest, session: Session = Depends(get_db)) -> RunSummary:
    run = create_regulation_run(
        session=session,
        title=payload.title,
        source=payload.source,
        body_text=payload.body_text,
    )
    report = build_report(session, run)

    return RunSummary(
        run_id=run.id,
        status=run.status,
        regulation_title=payload.title,
        obligations_count=len(report["obligations"]),
        mappings_count=len(report["mappings"]),
        review_required=run.review_required,
    )


@router.get("", response_model=list[RunSummary])
def list_all_runs(session: Session = Depends(get_db)) -> list[RunSummary]:
    runs = list_runs(session)
    summaries: list[RunSummary] = []

    for run in runs:
        report = build_report(session, run)
        summaries.append(
            RunSummary(
                run_id=run.id,
                status=run.status,
                regulation_title=run.regulation.title,
                obligations_count=len(report["obligations"]),
                mappings_count=len(report["mappings"]),
                review_required=run.review_required,
            )
        )

    return summaries


@router.get("/{run_id}")
def get_run_details(run_id: str, session: Session = Depends(get_db)) -> dict:
    run = get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return build_report(session, run)
