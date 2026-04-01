from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from controldiff.api.deps import get_db
from controldiff.domain.enums import ReviewDecisionType
from controldiff.services.regulation_service import get_run
from controldiff.services.review_service import apply_review_decision

router = APIRouter(prefix="/api/v1/runs", tags=["review"])


class ReviewRequest(BaseModel):
    reviewer: str = Field(min_length=2, max_length=128)
    decision: ReviewDecisionType
    notes: str = ""


@router.post("/{run_id}/review")
def review_run(run_id: str, payload: ReviewRequest, session: Session = Depends(get_db)) -> dict[str, str]:
    run = get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    updated = apply_review_decision(
        session=session,
        run=run,
        reviewer=payload.reviewer,
        decision=payload.decision,
        notes=payload.notes,
    )
    return {"run_id": updated.id, "status": updated.status}
