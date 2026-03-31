from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from controldiff.agents.nodes.control_mapper import map_obligation_to_controls
from controldiff.agents.nodes.obligation_extractor import extract_obligations
from controldiff.agents.schemas import Obligation
from controldiff.domain.enums import RunStatus
from controldiff.domain.models import MappingRecord, ObligationRecord, RegulationDocument, WorkflowRun
from controldiff.retrieval.control_search import retrieve_candidate_controls


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
    stored_obligations: list[Obligation] = []

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
        stored_obligations.append(obligation)

    session.commit()

    total_confidence = 0.0
    total_mappings = 0

    for obligation in stored_obligations:
        candidates = retrieve_candidate_controls(session, obligation.text)
        mappings = map_obligation_to_controls(obligation, candidates)

        for mapping in mappings:
            session.add(
                MappingRecord(
                    run_id=run.id,
                    obligation_id=mapping.obligation_id,
                    control_id=mapping.control_id,
                    impact=mapping.impact,
                    confidence=mapping.confidence,
                    rationale=mapping.rationale,
                    citations_json=json.dumps(
                        [citation.model_dump() for citation in mapping.citations]
                    ),
                    needs_review=False,
                )
            )
            total_confidence += mapping.confidence
            total_mappings += 1

    if total_mappings > 0:
        run.confidence = total_confidence / total_mappings

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
            selectinload(WorkflowRun.mappings),
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
            selectinload(WorkflowRun.mappings),
        )
        .where(WorkflowRun.id == run_id)
    )
    return session.scalars(statement).first()
