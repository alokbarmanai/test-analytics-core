import pytest
from src.exceptions import InvalidReportSchemaError
from src.parser import load_test_results

from src.parser import calculate_metrics


def test_calculate_metrics_success():
    # Sample test data
    test_data = [
        {"name": "test1", "status": "passed", "retries": 0},
        {"name": "test2", "status": "failed", "retries": 1},
        {"name": "test3", "status": "passed", "retries": 0},
        {"name": "test4", "status": "failed", "retries": 2},
    ]

    # Expected metrics
    expected_metrics = {
        "total": 4,
        "passed": 2,
        "failed": 2,
        "pass_rate_percentage": 50.0,
        "flaky_tests": ["test2", "test4"],
    }

    # Call the function and assert the results
    actual_metrics = calculate_metrics(test_data)
    assert actual_metrics == expected_metrics
    assert "total" in actual_metrics
    assert actual_metrics["total"] == 4


def test_load_test_results_invalid_schema(tmp_path):
    # 1. Create a temporary file with malformed JSON data (missing the "tests" key)
    bad_data_file = tmp_path / "corrupted_report.json"
    bad_data_file.write_text('{"project": "Broken API", "environment": "dev"}')

    # 2. Use the pytest exception wrapper to watch for the custom error
    with pytest.raises(InvalidReportSchemaError) as exc_info:
        load_test_results(str(bad_data_file))

    # 3. Optional: Verify that your helpful error message text is present
    # assert "Validation Failed" in str(exc_info.value)  # this line will be failed
    assert "Invalid report" in str(exc_info.value)
