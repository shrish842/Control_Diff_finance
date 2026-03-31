from __future__ import annotations

from controldiff.agents.nodes.control_mapper import map_obligation_to_controls
from controldiff.agents.schemas import Citation, Obligation, RetrievedCandidate


def test_map_obligation_to_controls_returns_structured_mappings() -> None:
    obligation = Obligation(
        obligation_id="obl-1",
        text="Institutions shall screen customers against sanctions lists before onboarding.",
        category="sanctions",
        severity="high",
        citations=[Citation(source="unit-test", excerpt="screen customers against sanctions lists")],
    )

    candidates = [
        RetrievedCandidate(
            control_id=1,
            code="AML-SAN-002",
            name="Sanctions Screening",
            score=0.75,
            citation="Applicants must be screened against OFAC before approval.",
        )
    ]

    mappings = map_obligation_to_controls(obligation, candidates)

    assert len(mappings) == 1
    assert mappings[0].control_code == "AML-SAN-002"
    assert mappings[0].impact == "high"
    assert mappings[0].confidence >= 0.25
