import pytest  # pyright: ignore[reportMissingImports]
import responses
from src.http_client import RemoteTelemetrySyncClient


@pytest.fixture
def sync_client():
    # Pass a dummy URL; it won't actually be called over the internet
    return RemoteTelemetrySyncClient(base_url="https://mock-cloud-metrics.io")


@responses.activate
def test_sync_metrics_success_path(sync_client):
    # 1. Setup the Interception Gatekeeper: Mock a successful 200 OK post response
    responses.add(
        method=responses.POST,
        url="https://mock-cloud-metrics.io/v1/telemetry",
        json={"status": "accepted", "synced": True},
        status=200,
    )

    # 2. Execute target execution logic
    is_success = sync_client.sync_metrics_payload(
        stream_id="db_latency", average_metric=14.2
    )

    # 3. Assert component processes the server contract accurately
    assert is_success is True


@responses.activate
def test_sync_metrics_server_failure_path(sync_client):
    # Mock a critical 500 Internal Server Error boundary condition
    responses.add(
        method=responses.POST,
        url="https://mock-cloud-metrics.io/v1/telemetry",
        status=500,
    )

    # Execute and verify the client recovers safely instead of crashing your suite
    is_success = sync_client.sync_metrics_payload(
        stream_id="db_latency", average_metric=14.2
    )
    assert is_success is False
