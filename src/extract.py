"""Extract raw CSV files for the City Mart learning pipeline."""

from pathlib import Path

import pandas as pd


def read_csv(file_path: str | Path) -> pd.DataFrame:
    """Read one CSV file after checking that it exists and has rows."""
    csv_path = Path(file_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    if not csv_path.is_file():
        raise ValueError(f"CSV path is not a file: {csv_path}")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"CSV file is empty: {csv_path}")
    return df


def read_raw_sales_files(raw_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Read all daily sales CSV files from a raw data directory."""
    directory = Path(raw_dir)
    if not directory.exists():
        raise FileNotFoundError(f"Raw data directory not found: {directory}")

    csv_files = sorted(directory.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in raw data directory: {directory}")

    return {path.name: read_csv(path) for path in csv_files}
