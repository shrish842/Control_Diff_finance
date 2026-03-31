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

class RetrievedCandidate(BaseModel):
    control_id: int
    code: str
    name: str
    score: float
    citation: str


class ControlMapping(BaseModel):
    obligation_id: str
    control_id: int
    control_code: str
    control_name: str
    impact: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    citations: list[Citation] = Field(default_factory=list)