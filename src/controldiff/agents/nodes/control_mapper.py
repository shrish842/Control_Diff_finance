from __future__ import annotations

from controldiff.agents.schemas import Citation, ControlMapping, Obligation, RetrievedCandidate


def map_obligation_to_controls(
    obligation: Obligation,
    candidates: list[RetrievedCandidate],
) -> list[ControlMapping]:
    mappings: list[ControlMapping] = []

    for candidate in candidates:
        if candidate.score >= 0.50:
            impact = "high"
        elif candidate.score >= 0.20:
            impact = "medium"
        else:
            impact = "low"

        confidence = min(0.99, max(0.25, candidate.score))

        mappings.append(
            ControlMapping(
                obligation_id=obligation.obligation_id,
                control_id=candidate.control_id,
                control_code=candidate.code,
                control_name=candidate.name,
                impact=impact,
                confidence=confidence,
                rationale=(
                    f"Matched obligation '{obligation.obligation_id}' to control "
                    f"'{candidate.code}' using lexical overlap against control text."
                ),
                citations=[
                    *obligation.citations,
                    Citation(source=f"control:{candidate.code}", excerpt=candidate.citation),
                ],
            )
        )

    return mappings
