"""Extract layer for reading raw sales CSV files."""

from pathlib import Path

import pandas as pd


def extract_sales_csv(file_path: str | Path) -> pd.DataFrame:
    """Read a sales CSV file and return its contents as a DataFrame.

    Args:
        file_path: Path to the raw CSV file.

    Returns:
        DataFrame containing raw sales rows.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the file is empty.
    """
    csv_path = Path(file_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"CSV file is empty: {csv_path}")

    return df
