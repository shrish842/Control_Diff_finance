from __future__ import annotations

import re
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from controldiff.agents.schemas import RetrievedCandidate
from controldiff.domain.models import Control

def _tokenize(test: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _keyword_score(query: str, text: str) -> float:
    query_tokens = query.lower().split()
    text_tokens = text.lower().split()

    if not query_tokens or not text_tokens:
        return 0.0

    query_counts = Counter(query_tokens)
    text_counts = Counter(text_tokens)

    overlap = sum(min(query_counts[token], text_counts[token]) for token in query_counts)
    return overlap / max(len(query_tokens), 1)


def retrieve_candidate_controls(
    session: Session,
    obligation_text: str,
    limit: int = 3,
) -> list[RetrievedCandidate]:
    controls = session.scalars(select(Control).where(Control.active.is_(True))).all()

    ranked: list[RetrievedCandidate] = []
    for control in controls:
        score = _keyword_score(
            obligation_text,
            f"{control.code} {control.name} {control.description} {control.policy_text}",
        )
        if score <= 0:
            continue

        ranked.append(
            RetrievedCandidate(
                control_id=control.id,
                code=control.code,
                name=control.name,
                score=min(score, 0.99),
                citation=control.policy_text[:180],
            )
        )

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:limit]
