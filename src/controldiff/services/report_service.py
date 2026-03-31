from __future__ import annotations

import json

from sqlalchemy.orm import Session

from controldiff.domain.models import MappingRecord, ObligationRecord, WorkflowRun


def build_report(session: Session, run: WorkflowRun) -> dict:
    obligations = (
        session.query(ObligationRecord)
        .filter(ObligationRecord.run_id == run.id)
        .all()
    )
    mappings = (
        session.query(MappingRecord)
        .filter(MappingRecord.run_id == run.id)
        .all()
    )

    payload = json.loads(run.payload_json)

    return {
        "run_id": run.id,
        "status": run.status,
        "confidence": run.confidence,
        "review_required": run.review_required,
        "final_report": run.final_report,
        "regulation": {
            "id": run.regulation.id,
            "title": run.regulation.title,
            "source": run.regulation.source,
            "body_text": run.regulation.body_text,
        },
        "obligations": [
            {
                "obligation_id": item.obligation_id,
                "text": item.text,
                "category": item.category,
                "severity": item.severity,
            }
            for item in obligations
        ],
        "mappings": [
            {
                "obligation_id": item.obligation_id,
                "control_id": item.control_id,
                "impact": item.impact,
                "confidence": item.confidence,
                "rationale": item.rationale,
                "needs_review": item.needs_review,
            }
            for item in mappings
        ],
        "payload": payload,
    }
