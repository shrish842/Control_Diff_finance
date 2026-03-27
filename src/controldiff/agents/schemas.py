from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    excerpt: str


class Obligation(BaseModel):
    obligation_id: str
    text: str
    category: str
    severity: str
    citations: list[Citation] = Field(default_factory=list)
