from __future__ import annotations

from pydantic import BaseModel, Field

from controldiff.domain.enums import RunStatus


class CreateRunRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    source: str = Field(min_length=3, max_length=255)
    body_text: str = Field(min_length=20)


class RunSummary(BaseModel):
    run_id: str
    status: RunStatus
    regulation_title: str
    obligations_count: int = 0
    mappings_count: int = 0
    review_required: bool = False
