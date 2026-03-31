from __future__ import annotations

from sqlalchemy.orm import Session

from controldiff.domain.models import Control
from controldiff.retrieval.control_search import retrieve_candidate_controls


def test_retrieve_candidate_controls_returns_matches(db_session: Session) -> None:
    existing = db_session.query(Control).all()
    if not existing:
        db_session.add(
            Control(
                code="AML-SAN-002",
                name="Sanctions Screening",
                description="Screen all customers against sanctions lists before onboarding.",
                policy_text="Applicants must be screened against OFAC before approval.",
            )
        )
        db_session.commit()

    candidates = retrieve_candidate_controls(
        db_session,
        "Institutions shall screen customers against sanctions lists before onboarding.",
    )

    assert len(candidates) >= 1
    assert any(candidate.code == "AML-SAN-002" for candidate in candidates)
