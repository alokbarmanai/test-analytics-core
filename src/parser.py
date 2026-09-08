import json
import logging
from typing import Any, Dict, List, cast

from src.exceptions import InvalidReportSchemaError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_test_results(file_path: str) -> List[Dict[str, Any]]:
    # logic here to open the file and return the test array
    with open(file_path, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "tests" not in data:
        raise InvalidReportSchemaError(
            "Invalid report schema: the JSON object must contain a 'tests' key."
        )
    if not isinstance(data["tests"], list):
        raise InvalidReportSchemaError(
            "Invalid report schema: the 'tests' value must be a list."
        )
    # 2. Tell mypy: "Trust me, I guarantee this specific key contains a List"
    test_list = cast(List[Dict[str, Any]], data["tests"])
    return test_list


def calculate_metrics(tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    # logic here to calculate metrics from the test results
    total_tests = len(tests)
    passed_tests = sum(1 for result in tests if result.get("status") == "passed")
    failed_tests = total_tests - passed_tests
    pass_rate_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    # "Loop through the tests and collect the name of every test that has retries > 0. Store these names in a list."
    flaky_tests = [
        result.get("name") for result in tests if result.get("retries", 0) > 0
    ]
    return {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "pass_rate_percentage": pass_rate_percentage,
        "flaky_tests": flaky_tests,
    }


# if __name__ == "__main__":
#     # 1. Define the relative path to your mock data
#     mock_data_path = "data/raw_test_data.json"

#     logger.info("--- Starting Test Analytics Execution ---")
#     logger.info(f"Loading test results from {mock_data_path}...")
#     try:
#         # 2. Parse the file
#         parsed_tests = load_test_results(mock_data_path)
#         # 3. Calculate metrics
#         analytics_summary = calculate_metrics(parsed_tests)
#         # 4. Print the final dashboard summary
#         # 1. Format the dictionary as a pretty, indented string
#         pretty_summary = json.dumps(analytics_summary, indent=2)
#         # 2. Log it out cleanly using logger.info
#         logger.info(f"Analytics Processed Successfully:\n{pretty_summary}")

#     except Exception as e:
#         logger.error(f"An error occurred while processing the test results: {e}")
