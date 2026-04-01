from __future__ import annotations

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from controldiff.agents.nodes.control_mapper import map_obligation_to_controls
from controldiff.agents.nodes.obligation_extractor import extract_obligations
from controldiff.agents.state import ControlDiffState
from controldiff.domain.enums import RunStatus
from controldiff.retrieval.control_search import retrieve_candidate_controls


def build_graph(session: Session):
    workflow = StateGraph(ControlDiffState)

    def extract_node(state: ControlDiffState) -> ControlDiffState:
        obligations = extract_obligations(
            state["regulation_text"],
            state["regulation_source"],
        )
        return {"obligations": obligations}

    def retrieve_node(state: ControlDiffState) -> ControlDiffState:
        candidates_by_obligation: dict[str, list] = {}

        for obligation in state.get("obligations", []):
            candidates_by_obligation[obligation.obligation_id] = retrieve_candidate_controls(
                session,
                obligation.text,
            )

        return {"candidates_by_obligation": candidates_by_obligation}

    def map_node(state: ControlDiffState) -> ControlDiffState:
        mappings = []

        for obligation in state.get("obligations", []):
            candidates = state.get("candidates_by_obligation", {}).get(
                obligation.obligation_id,
                [],
            )
            mappings.extend(map_obligation_to_controls(obligation, candidates))

        confidence = 0.0
        if mappings:
            confidence = sum(mapping.confidence for mapping in mappings) / len(mappings)

        return {
            "mappings": mappings,
            "confidence": confidence,
            "status": RunStatus.COMPLETED.value,
        }

    workflow.add_node("extract_obligations", extract_node)
    workflow.add_node("retrieve_controls", retrieve_node)
    workflow.add_node("map_controls", map_node)

    workflow.set_entry_point("extract_obligations")
    workflow.add_edge("extract_obligations", "retrieve_controls")
    workflow.add_edge("retrieve_controls", "map_controls")
    workflow.add_edge("map_controls", END)

    return workflow.compile()
