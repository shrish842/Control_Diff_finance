from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from controldiff.agents.nodes.obligation_extractor import extract_obligations
from controldiff.domain.enums import RunStatus
from controldiff.domain.models import ObligationRecord, RegulationDocument, WorkflowRun


def create_regulation_run(
    session: Session,
    title: str,
    source: str,
    body_text: str,
) -> WorkflowRun:
    regulation = RegulationDocument(
        title=title,
        source=source,
        body_text=body_text,
    )
    session.add(regulation)
    session.commit()
    session.refresh(regulation)

    run = WorkflowRun(
        regulation_id=regulation.id,
        status=RunStatus.PENDING.value,
        confidence=0.0,
        review_required=False,
        final_report="",
        payload_json="{}",
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    obligations = extract_obligations(body_text, source)

    for obligation in obligations:
        session.add(
            ObligationRecord(
                obligation_id=obligation.obligation_id,
                run_id=run.id,
                regulation_id=regulation.id,
                text=obligation.text,
                category=obligation.category,
                severity=obligation.severity,
                citations_json=json.dumps(
                    [citation.model_dump() for citation in obligation.citations]
                ),
            )
        )

    run.status = RunStatus.COMPLETED.value
    session.add(run)
    session.commit()

    stored_run = get_run(session, run.id)
    if stored_run is None:
        raise RuntimeError("Newly created workflow run could not be reloaded.")

    return stored_run


def list_runs(session: Session) -> list[WorkflowRun]:
    statement = (
        select(WorkflowRun)
        .options(
            selectinload(WorkflowRun.regulation),
            selectinload(WorkflowRun.obligations),
        )
        .order_by(WorkflowRun.created_at.desc())
    )
    return list(session.scalars(statement))


def get_run(session: Session, run_id: str) -> WorkflowRun | None:
    statement = (
        select(WorkflowRun)
        .options(
            selectinload(WorkflowRun.regulation),
            selectinload(WorkflowRun.obligations),
        )
        .where(WorkflowRun.id == run_id)
    )
    return session.scalars(statement).first()
