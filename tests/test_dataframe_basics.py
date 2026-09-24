import pandas as pd
import pytest  # pyright: ignore[reportMissingImports]

from src.data_processor import (
    aggregate_environment_metrics,
    clean_and_sanitize_telemetry,
    ingest_and_profile_runs,
)


@pytest.fixture
def telemetry_raw_dataset():
    # A mock array mimicking multiple automated test suite execution parameters
    return [
        {"suite_id": "auth_suite", "duration_ms": 1250, "passed": True},
        {"suite_id": "api_gateway", "duration_ms": 4800, "passed": False},
        {"suite_id": "db_migration", "duration_ms": 3100, "passed": True},
    ]


def test_dataframe_structural_dimensions(telemetry_raw_dataset):
    df, metrics = ingest_and_profile_runs(telemetry_raw_dataset)

    # 1. Assert structural dimensions are calculated correctly
    assert metrics["total_records"] == 3
    assert metrics["total_attributes"] == 3

    # 2. Verify column labels are present precisely as expected
    assert "duration_ms" in metrics["columns_list"]
    assert "passed" in metrics["columns_list"]

    # 3. Verify underlying type conversion (pandas Series type checking)
    # Hint: 'df["column_name"]' extracts a single Series vector.
    assert isinstance(df, pd.DataFrame)
    assert df["duration_ms"].dtype in ["int64", "int32"]


def test_telemetry_cleansing_pipeline():
    # Construct a dataset riddled with typical log corruption edge cases
    corrupted_dataset = [
        {"suite_id": "auth_suite", "duration_ms": 1500},
        {"suite_id": "api_gateway", "duration_ms": None},  # Missing duration
        {
            "suite_id": None,
            "duration_ms": 3200,
        },  # Missing identifier (should be dropped)
    ]

    # Ingest baseline dataframe
    raw_df = pd.DataFrame(corrupted_dataset)

    # Execute transformation pipeline
    sanitized_df = clean_and_sanitize_telemetry(raw_df)

    # 1. Assert row filtering boundary: The row with None suite_id must be completely removed
    # The final dataset length should shrink from 3 rows down to 2 rows
    assert len(sanitized_df) == 2

    # 2. Assert value filling: The None duration_ms for api_gateway must be filled with 0.0
    # We use .loc to search by column condition cleanly in pandas: df.loc[row_condition, column_name]
    api_gateway_row = sanitized_df[sanitized_df["suite_id"] == "api_gateway"]
    # .item() extracts the single value out of the matching vector series
    assert float(api_gateway_row["duration_ms"].item()) == 0.0


def test_environment_metrics_aggregation():
    # A multi-environment dataset simulating real execution matrices
    mixed_dataset = [
        {
            "environment": "production",
            "suite_id": "auth",
            "duration_ms": 1000,
            "passed": True,
        },
        {
            "environment": "production",
            "suite_id": "api",
            "duration_ms": 2000,
            "passed": False,
        },
        {
            "environment": "staging",
            "suite_id": "auth",
            "duration_ms": 1500,
            "passed": True,
        },
        {
            "environment": "staging",
            "suite_id": "db",
            "duration_ms": 1500,
            "passed": True,
        },
    ]

    raw_df = pd.DataFrame(mixed_dataset)

    # Execute the aggregation pipeline engine
    aggregated_df = aggregate_environment_metrics(raw_df)

    # 1. Assert table reduction: 4 rows should collapse down into 2 unique environment rows
    assert len(aggregated_df) == 2

    # 2. Verify metric calculation accuracy for 'production'
    prod_row = aggregated_df[aggregated_df["environment"] == "production"].iloc[0]
    assert prod_row["total_runs"] == 2
    assert prod_row["average_duration"] == 1500.0  # (1000 + 2000) / 2
    assert prod_row["pass_rate"] == 50.0  # 1 success out of 2 runs

    # 3. Verify metric calculation accuracy for 'staging'
    staging_row = aggregated_df[aggregated_df["environment"] == "staging"].iloc[0]
    assert staging_row["total_runs"] == 2
    assert staging_row["pass_rate"] == 100.0  # 2 successes out of 2 runs
