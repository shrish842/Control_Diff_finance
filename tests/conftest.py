from __future__ import annotations

import pathlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from controldiff.api.main import app
from controldiff.db.base import Base
from controldiff.db.session import SessionLocal, engine
from controldiff.domain.models import (
    Control,
    MappingRecord,
    ObligationRecord,
    PolicyVersion,
    RegulationDocument,
    ReviewDecision,
    WorkflowRun,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_artifacts() -> None:
    pathlib.Path("artifacts").mkdir(exist_ok=True)
    pathlib.Path("data/raw").mkdir(parents=True, exist_ok=True)
    pathlib.Path("data/processed").mkdir(parents=True, exist_ok=True)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        for model in (
            ReviewDecision,
            MappingRecord,
            ObligationRecord,
            WorkflowRun,
            RegulationDocument,
            PolicyVersion,
            Control,
        ):
            session.execute(delete(model))

        controls = [
            Control(
                code="AML-CIP-001",
                name="Customer Identity Verification",
                description="Verify customer identities before account activation.",
                policy_text="Analysts must verify identity using approved evidence.",
            ),
            Control(
                code="AML-SAN-002",
                name="Sanctions Screening",
                description="Screen all customers against sanctions lists before onboarding.",
                policy_text="Applicants must be screened against OFAC before approval.",
            ),
            Control(
                code="AML-BO-003",
                name="Beneficial Ownership Review",
                description="Identify and verify beneficial owners for legal-entity customers above applicable thresholds.",
                policy_text="Business customers must provide beneficial owner information and supporting evidence.",
            ),
        ]

        session.add_all(controls)
        session.commit()

        for control in controls:
            session.add(
                PolicyVersion(
                    control_id=control.id,
                    version_label="v1",
                    content=control.policy_text,
                )
            )
        session.commit()

        yield session


@pytest.fixture()
def client(db_session):
    return TestClient(app)
