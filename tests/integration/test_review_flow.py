from __future__ import annotations


def test_report_endpoint_returns_graph_outputs(client) -> None:
    create_response = client.post(
        "/api/v1/runs",
        json={
            "title": "AML Bulletin",
            "source": "integration-test",
            "body_text": (
                "Financial institutions must identify beneficial owners for legal-entity customers. "
                "They shall screen customers against sanctions lists prior to onboarding. "
                "Manual review notes must document enhanced due diligence decisions."
            ),
        },
    )
    assert create_response.status_code == 200
    run_id = create_response.json()["run_id"]

    report_response = client.get(f"/api/v1/runs/{run_id}/report")
    assert report_response.status_code == 200
    report = report_response.json()

    assert report["run_id"] == run_id
    assert report["regulation"]["title"] == "AML Bulletin"
    assert len(report["obligations"]) >= 1
    assert len(report["mappings"]) >= 1
    assert "critic_notes" in report
    assert "replay_summary" in report
    assert "diffs" in report


def test_review_endpoint_updates_run_status(client) -> None:
    create_response = client.post(
        "/api/v1/runs",
        json={
            "title": "CIP Update",
            "source": "integration-test",
            "body_text": (
                "Institutions must document identity verification steps before approving customer onboarding."
            ),
        },
    )
    assert create_response.status_code == 200
    run_id = create_response.json()["run_id"]

    review_response = client.post(
        f"/api/v1/runs/{run_id}/review",
        json={
            "reviewer": "Shrish",
            "decision": "approve",
            "notes": "Mappings look correct for the seeded controls.",
        },
    )
    assert review_response.status_code == 200
    review_payload = review_response.json()
    assert review_payload["run_id"] == run_id
    assert review_payload["status"] == "approved"

    report_response = client.get(f"/api/v1/runs/{run_id}/report")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["status"] == "approved"
    assert report["review_required"] is False
    assert len(report["reviews"]) == 1
    assert report["reviews"][0]["decision"] == "approve"
