from __future__ import annotations

from controldiff.agents.graph import build_graph


def test_graph_generates_obligations_and_mappings(db_session) -> None:
    graph = build_graph(db_session)

    result = graph.invoke(
        {
            "run_id": "run-graph-1",
            "regulation_id": "reg-graph-1",
            "regulation_title": "AML Bulletin",
            "regulation_source": "unit-test",
            "regulation_text": (
                "Financial institutions must identify beneficial owners for legal-entity customers. "
                "They shall screen customers against sanctions lists prior to onboarding."
            ),
        }
    )

    assert result["obligations"]
    assert result["mappings"]
    assert result["confidence"] > 0
    assert result["status"] == "completed"
