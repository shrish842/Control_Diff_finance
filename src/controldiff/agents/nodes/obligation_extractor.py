from __future__ import annotations

import re

from controldiff.agents.schemas import Citation, Obligation

# Ordered from most specific to most general so we do not classify
# "identify beneficial owners" as generic CIP before checking the
# more informative beneficial-ownership phrase.
CATEGORY_PATTERNS: list[tuple[str, str]] = [
    ("beneficial owners", "beneficial_ownership"),
    ("beneficial owner", "beneficial_ownership"),
    ("ofac", "sanctions"),
    ("sanctions", "sanctions"),
    ("sanction", "sanctions"),
    ("manual review", "manual_review"),
    ("identity verification", "cip"),
    ("identify", "cip"),
    ("identity", "cip"),
    ("documents", "kyc"),
    ("document", "kyc"),
]


def detect_category(sentence: str) -> str | None:
    lower_sentence = sentence.lower()
    for pattern, category in CATEGORY_PATTERNS:
        if pattern in lower_sentence:
            return category
    return None


def extract_obligations(text: str, source: str) -> list[Obligation]:
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    obligations: list[Obligation] = []
    index = 1

    for sentence in sentences:
        if not sentence:
            continue

        category = detect_category(sentence)
        if category is None:
            continue

        lower_sentence = sentence.lower()
        severity = (
            "high"
            if any(token in lower_sentence for token in ("must", "shall", "required"))
            else "medium"
        )

        obligations.append(
            Obligation(
                obligation_id=f"obl-{index}",
                text=sentence,
                category=category,
                severity=severity,
                citations=[Citation(source=source, excerpt=sentence[:240])],
            )
        )
        index += 1

    if obligations:
        return obligations

    fallback_excerpt = " ".join(text.split())[:300]
    return [
        Obligation(
            obligation_id="obl-1",
            text=f"Review the regulation update for AML onboarding impact. {fallback_excerpt}",
            category="general",
            severity="medium",
            citations=[Citation(source=source, excerpt=fallback_excerpt)],
        )
    ]
