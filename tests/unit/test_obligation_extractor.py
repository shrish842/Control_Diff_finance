from __future__ import annotations

from controldiff.agents.nodes.obligation_extractor import extract_obligations


def test_extract_obligations_finds_regulatory_sentences() -> None:
    text = (
        "Financial institutions must identify beneficial owners for legal-entity customers. "
        "They shall screen customers against OFAC sanctions lists before onboarding. "
        "A welcome email may be sent after approval."
    )

    obligations = extract_obligations(text, "unit-test")

    assert len(obligations) >= 2
    assert any(item.category == "beneficial_ownership" for item in obligations)
    assert any(item.category == "sanctions" for item in obligations)
    assert all(item.citations for item in obligations)
