import pytest  # pyright: ignore[reportMissingImports]

from src.analytics import InvalidPayloadError, verify_and_process_payload


def test_pydantic_valid_payload():
    payload = {"metric_name": "cpu_usage", "values": [10, 20, 30]}
    result = verify_and_process_payload(payload)
    # Assert that the logic processes correctly
    assert result["status"] == "PROCESSED"
    assert result["average"] == 20.0


def test_pydantic_type_mismatch_exception():
    # Pass a string instead of an iterable list to trigger Pydantic's type gatekeeper
    payload = {"metric_name": "cpu_usage", "values": "not_a_list"}

    with pytest.raises(InvalidPayloadError) as exc_info:
        verify_and_process_payload(payload)

    assert "Schema validation failed" in str(exc_info.value)


def test_pydantic_empty_string_boundary():
    # Pass an empty string for the metric name to break the min_length=1 constraint
    payload = {"metric_name": "", "values": [10, 20, 30]}

    with pytest.raises(InvalidPayloadError) as exc_info:
        verify_and_process_payload(payload)

    # Assert that Pydantic intercepts the short length boundary properly
    assert "String should have at least 1 character" in str(exc_info.value)
