from __future__ import annotations

from typing import TypedDict

from controldiff.agents.schemas import ControlMapping, Obligation, RetrievedCandidate


class ControlDiffState(TypedDict, total=False):
    run_id: str
    regulation_id: str
    regulation_title: str
    regulation_source: str
    regulation_text: str
    obligations: list[Obligation]
    candidates_by_obligation: dict[str, list[RetrievedCandidate]]
    mappings: list[ControlMapping]
    confidence: float
    status: str
