import pandas as pd


def ingest_and_profile_runs(raw_data: list[dict]) -> tuple[pd.DataFrame, dict]:
    # 4.1: Convert standard raw dictionary array into a pandas DataFrame grid
    df = pd.DataFrame(raw_data)

    # Extract structural metrics using native pandas properties
    metrics = {
        "total_records": int(df.shape[0]),  # Number of rows
        "total_attributes": int(df.shape[1]),  # Number of columns
        "columns_list": list(df.columns),  # List of column names
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
    }
    return df, metrics


def clean_and_sanitize_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    # Create an explicit copy to protect the original dataframe from side effects
    cleaned_df = df.copy()

    # 1. Handle missing values: Fill empty 'duration_ms' entries with a fallback value of 0.0
    if "duration_ms" in cleaned_df.columns:
        cleaned_df["duration_ms"] = cleaned_df["duration_ms"].fillna(0.0)
        # Type correction: Explicitly cast the column to a predictable float type
        cleaned_df["duration_ms"] = cleaned_df["duration_ms"].astype(float)

    # 2. Filter out records: Remove any rows where 'suite_id' is missing or None
    if "suite_id" in cleaned_df.columns:
        cleaned_df = cleaned_df.dropna(subset=["suite_id"])

    return cleaned_df


def aggregate_environment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Group data by 'environment' and compute structural metrics for each group
    # We pass a dictionary to .agg() mapping columns to the math operations we want
    summary_df = (
        df.groupby("environment")
        .agg(
            total_runs=("suite_id", "count"),
            average_duration=("duration_ms", "mean"),
            successful_runs=("passed", "sum"),
        )
        .reset_index()
    )  # Flatten the index back to a standard 2D table grid

    # 2. Calculate a custom dynamic column across the summarized matrix blocks
    summary_df["pass_rate"] = (
        summary_df["successful_runs"] / summary_df["total_runs"]
    ) * 100.0

    return summary_df
