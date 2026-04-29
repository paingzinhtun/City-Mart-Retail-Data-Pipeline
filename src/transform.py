"""Transform layer for cleaning and validating retail sales data."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "customer_name",
    "customer_email",
    "customer_phone",
    "store_id",
    "store_name",
    "store_city",
    "product_id",
    "product_name",
    "category_id",
    "category_name",
    "supplier_id",
    "supplier_name",
    "quantity",
    "unit_price",
    "payment_method",
]


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, type-cast, validate, and enrich raw sales data.

    Args:
        df: Raw sales DataFrame from the extract layer.

    Returns:
        Cleaned DataFrame ready for OLTP loading.

    Raises:
        ValueError: If required columns are missing or validation fails.
    """
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    cleaned = df.copy()

    # Trim whitespace in text fields before duplicate checks and loading.
    text_columns = cleaned.select_dtypes(include=["object"]).columns
    for column in text_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    cleaned = cleaned.dropna(subset=REQUIRED_COLUMNS)
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], errors="raise").dt.date
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="raise").astype(int)
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="raise").astype(float)

    invalid_quantity = cleaned[cleaned["quantity"] <= 0]
    if not invalid_quantity.empty:
        raise ValueError("Validation failed: quantity must be greater than 0")

    invalid_price = cleaned[cleaned["unit_price"] < 0]
    if not invalid_price.empty:
        raise ValueError("Validation failed: unit_price must be greater than or equal to 0")

    cleaned["line_total"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned = cleaned.drop_duplicates(subset=["order_id", "product_id"])
    cleaned = cleaned.sort_values(["order_date", "order_id", "product_id"]).reset_index(drop=True)

    return cleaned


def save_processed_data(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save transformed data to a processed CSV file.

    Args:
        df: Transformed sales DataFrame.
        output_path: Destination file path.
    """
    processed_path = Path(output_path)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
