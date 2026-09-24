import pytest  # pyright: ignore[reportMissingImports]  # Block 2: Third-party (Alphabetical)

# Blank line separating blocks
from src.analytics import (
    InvalidPayloadError,
    verify_and_process_payload,
)  # Block 3: Local app imports (Combined & Sorted)


@pytest.fixture
def baseline_payload():
    return {"metric_name": "cpu_usage", "values": [10, 20, 30]}


# Pass a valid payload dictionary (e.g., {"metric_name": "cpu_usage", "values": [10, 20, 30]}).
# Assert that the returned dictionary matches the exact expected schema structure and values perfectly.
def test_successful_payload_assertion(baseline_payload):
    result = verify_and_process_payload(baseline_payload)
    assert result["metric"] == "cpu_usage"
    assert result["status"] == "PROCESSED"
    assert result["average"] == 20.0


# Pass a payload where values is an empty list [].
# Verify the returned structure handles the boundary condition and correctly outputs a status of "EMPTY".
def test_empty_values_boundary(baseline_payload):
    payload = baseline_payload.copy()
    payload["values"] = []
    result = verify_and_process_payload(payload)
    assert result["metric"] == "cpu_usage"
    assert result["status"] == "EMPTY"
    assert result["average"] == 0.0


# Pass an invalid payload missing the "metric_name" key.
# Use pytest.raises to assert that InvalidPayloadError is raised, and verify that the error text contains "Missing required payload fields".
def test_missing_keys_exception(baseline_payload):
    payload = baseline_payload.copy()
    del payload["metric_name"]

    with pytest.raises(InvalidPayloadError) as exc_info:
        verify_and_process_payload(payload)
    assert isinstance(exc_info.value, InvalidPayloadError)
    assert "Field required" in str(exc_info.value)


# Pass a payload where "values" is passed as a single integer instead of a list.
# Assert that InvalidPayloadError is successfully caught and checked.
def test_invalid_schema_type_exception(baseline_payload):
    payload = baseline_payload.copy()
    payload["values"] = 50

    with pytest.raises(InvalidPayloadError) as exc_info:
        verify_and_process_payload(payload)
    assert "Input should be a valid list" in str(exc_info.value)
