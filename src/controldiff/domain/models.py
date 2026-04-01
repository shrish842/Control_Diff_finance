from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from controldiff.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class RegulationDocument(TimestampMixin, Base):
    __tablename__ = "regulation_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(255))
    body_text: Mapped[str] = mapped_column(Text)

    runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="regulation")


class Control(TimestampMixin, Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(128), default="aml_onboarding")
    owner: Mapped[str] = mapped_column(String(128), default="Compliance")
    description: Mapped[str] = mapped_column(Text)
    policy_text: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    policy_versions: Mapped[list["PolicyVersion"]] = relationship(back_populates="control")


class PolicyVersion(TimestampMixin, Base):
    __tablename__ = "policy_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"))
    version_label: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)

    control: Mapped["Control"] = relationship(back_populates="policy_versions")


class WorkflowRun(TimestampMixin, Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_id: Mapped[str] = mapped_column(ForeignKey("regulation_documents.id"))
    status: Mapped[str] = mapped_column(String(64), default="pending")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    final_report: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")

    regulation: Mapped["RegulationDocument"] = relationship(back_populates="runs")
    obligations: Mapped[list["ObligationRecord"]] = relationship(back_populates="run")
    mappings: Mapped[list["MappingRecord"]] = relationship(back_populates="run")
    reviews: Mapped[list["ReviewDecision"]] = relationship(back_populates="run")


class ObligationRecord(TimestampMixin, Base):
    __tablename__ = "obligation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    obligation_id: Mapped[str] = mapped_column(String(64), index=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    regulation_id: Mapped[str] = mapped_column(ForeignKey("regulation_documents.id"))
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(128))
    severity: Mapped[str] = mapped_column(String(32))
    citations_json: Mapped[str] = mapped_column(Text, default="[]")

    run: Mapped["WorkflowRun"] = relationship(back_populates="obligations")


class MappingRecord(TimestampMixin, Base):
    __tablename__ = "mapping_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    obligation_id: Mapped[str] = mapped_column(String(64), index=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"))
    impact: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    rationale: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[str] = mapped_column(Text, default="[]")
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)

    run: Mapped["WorkflowRun"] = relationship(back_populates="mappings")
    control: Mapped["Control"] = relationship()


class ReplayCase(TimestampMixin, Base):
    __tablename__ = "replay_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    customer_segment: Mapped[str] = mapped_column(String(64))
    risk_level: Mapped[str] = mapped_column(String(32))
    triggered_controls_json: Mapped[str] = mapped_column(Text, default="[]")
    review_outcome: Mapped[str] = mapped_column(String(64))


class ReviewDecision(TimestampMixin, Base):
    __tablename__ = "review_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    reviewer: Mapped[str] = mapped_column(String(128))
    decision: Mapped[str] = mapped_column(String(32))
    notes: Mapped[str] = mapped_column(Text, default="")

    run: Mapped["WorkflowRun"] = relationship(back_populates="reviews")
