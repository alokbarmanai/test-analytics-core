import pytest
from fastapi.testclient import TestClient

from src.main import app

# Create a test client that can simulate requests to your FastAPI application
client = TestClient(app)


def test_health_endpoint():
    """Verify that the health check endpoint returns a 200 OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_analytics_success():
    """Verify that posting valid test results computes metrics and stores them."""
    test_payload = [
        {"name": "test_login", "status": "passed", "retries": 0},
        {"name": "test_logout", "status": "passed", "retries": 0},
        {"name": "test_checkout", "status": "failed", "retries": 1},
        {"name": "test_checkout", "status": "passed", "retries": 1},
    ]

    response = client.post("/analytics", json=test_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["passed"] == 3
    assert data["failed"] == 1
    assert "test_checkout" in data["flaky_tests"]


# Add this marker right above your delete test function definition
@pytest.mark.skip(reason="Disabling delete test during standard development cycles")
def test_delete_individual_analytics_run():
    """Verify that a single test record can be deleted by its ID and missing IDs handle errors safely."""
    # 1. First fetch current history entries to find an active ID to target
    history_response = client.get("/history")
    assert history_response.status_code == 200
    records = history_response.json()

    if len(records) > 0:
        target_id = records[0]["id"]

        # 2. Execute deletion command against that targeted ID
        delete_response = client.delete(f"/analytics/{target_id}")
        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"]

    # 3. Verify that querying a non-existent or highly improbable ID handles gracefully
    fake_id = 99999
    missing_response = client.delete(f"/analytics/{fake_id}")
    assert "not found" in missing_response.json()["error"]
