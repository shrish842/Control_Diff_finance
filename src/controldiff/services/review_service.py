from __future__ import annotations

from sqlalchemy.orm import Session

from controldiff.domain.enums import ReviewDecisionType, RunStatus
from controldiff.domain.models import ReviewDecision, WorkflowRun


def apply_review_decision(
    session: Session,
    run: WorkflowRun,
    reviewer: str,
    decision: ReviewDecisionType,
    notes: str,
) -> WorkflowRun:
    review = ReviewDecision(
        run_id=run.id,
        reviewer=reviewer,
        decision=decision.value,
        notes=notes,
    )

    run.review_required = False
    run.status = (
        RunStatus.APPROVED.value
        if decision == ReviewDecisionType.APPROVE
        else RunStatus.REJECTED.value
    )

    session.add(review)
    session.add(run)
    session.commit()
    session.refresh(run)
    return run
