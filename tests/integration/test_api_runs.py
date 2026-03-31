from __future__ import annotations


def test_create_run_and_list_runs(client) -> None:
    response = client.post(
        "/api/v1/runs",
        json={
            "title": "AML Bulletin",
            "source": "integration-test",
            "body_text": (
                "Financial institutions must identify beneficial owners for legal-entity customers. "
                "They shall screen customers against sanctions lists prior to onboarding."
            ),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["regulation_title"] == "AML Bulletin"
    assert payload["obligations_count"] >= 1
    
    detail_response = client.get(f"/api/v1/runs/{payload['run_id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert len(detail["mappings"]) >= 1

    assert payload["mappings_count"] >= 1
    

def test_get_run_detail(client) -> None:
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

    detail_response = client.get(f"/api/v1/runs/{run_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["run_id"] == run_id
    assert detail["regulation"]["title"] == "CIP Update"
    assert len(detail["obligations"]) >= 1
    assert len(detail["mappings"]) >= 1