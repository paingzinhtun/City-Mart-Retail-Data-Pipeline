"""Data quality checks for staging sales data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_PRODUCT_COLUMNS = ["product_id", "product_name", "category", "unit_sale_price_ks", "unit_cost_ks"]
REQUIRED_STORE_COLUMNS = ["store_id", "store_name", "store_city"]
REQUIRED_SALES_COLUMNS = [
    "sale_id",
    "sale_date",
    "store_id",
    "product_id",
    "units_sold",
    "unit_sale_price_ks",
    "unit_cost_ks",
    "revenue_ks",
    "profit_ks",
    "payment_method",
]


def validate_required_columns(df: pd.DataFrame, required_columns: list[str], table_name: str) -> list[str]:
    """Return required columns that are missing from a DataFrame."""
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        return [f"{table_name} is missing required columns: {missing}"]
    return []


def validate_missing_values(df: pd.DataFrame) -> dict[str, int]:
    """Count missing values per column."""
    return {column: int(count) for column, count in df.isna().sum().items() if int(count) > 0}


def build_validation_report(
    raw_frames: dict[str, pd.DataFrame],
    staging_products: pd.DataFrame,
    staging_stores: pd.DataFrame,
    staging_sales: pd.DataFrame,
) -> dict[str, Any]:
    """Build a JSON-serializable validation report for the pipeline run."""
    errors: list[str] = []
    errors.extend(validate_required_columns(staging_products, REQUIRED_PRODUCT_COLUMNS, "staging_products"))
    errors.extend(validate_required_columns(staging_stores, REQUIRED_STORE_COLUMNS, "staging_stores"))
    errors.extend(validate_required_columns(staging_sales, REQUIRED_SALES_COLUMNS, "staging_sales"))

    product_ids = set(staging_products.get("product_id", pd.Series(dtype=str)).dropna().astype(str))
    store_ids = set(staging_stores.get("store_id", pd.Series(dtype=str)).dropna().astype(str))
    sales_product_ids = set(staging_sales.get("product_id", pd.Series(dtype=str)).dropna().astype(str))
    sales_store_ids = set(staging_sales.get("store_id", pd.Series(dtype=str)).dropna().astype(str))

    duplicate_sale_id_count = int(staging_sales.duplicated(subset=["sale_id"]).sum())
    missing_value_counts = {
        file_name: validate_missing_values(df) for file_name, df in raw_frames.items()
    }
    staging_missing_value_counts = {
        "staging_products": validate_missing_values(staging_products),
        "staging_stores": validate_missing_values(staging_stores),
        "staging_sales": validate_missing_values(staging_sales),
    }

    invalid_unit_count = int((pd.to_numeric(staging_sales["units_sold"], errors="coerce") <= 0).sum())
    invalid_price_count = int(
        (
            (pd.to_numeric(staging_sales["unit_sale_price_ks"], errors="coerce") < 0)
            | (pd.to_numeric(staging_sales["unit_cost_ks"], errors="coerce") < 0)
        ).sum()
    )
    unknown_product_id_count = int(staging_sales["product_id"].astype(str).isin(sales_product_ids - product_ids).sum())
    unknown_store_id_count = int(staging_sales["store_id"].astype(str).isin(sales_store_ids - store_ids).sum())

    if duplicate_sale_id_count:
        errors.append(f"Found {duplicate_sale_id_count} duplicate sale_id values.")
    for table_name, counts in staging_missing_value_counts.items():
        if counts:
            errors.append(f"{table_name} has missing values: {counts}.")
    if invalid_unit_count:
        errors.append(f"Found {invalid_unit_count} rows where units_sold is not greater than 0.")
    if invalid_price_count:
        errors.append(f"Found {invalid_price_count} rows with negative sale price or cost.")
    if unknown_product_id_count:
        errors.append(f"Found {unknown_product_id_count} sales rows with unknown product_id.")
    if unknown_store_id_count:
        errors.append(f"Found {unknown_store_id_count} sales rows with unknown store_id.")

    return {
        "raw_row_counts": {file_name: int(len(df)) for file_name, df in raw_frames.items()},
        "staging_row_counts": {
            "staging_products": int(len(staging_products)),
            "staging_stores": int(len(staging_stores)),
            "staging_sales": int(len(staging_sales)),
        },
        "duplicate_sale_id_count": duplicate_sale_id_count,
        "missing_value_counts_per_file": missing_value_counts,
        "staging_missing_value_counts": staging_missing_value_counts,
        "invalid_price_count": invalid_price_count,
        "invalid_unit_count": invalid_unit_count,
        "unknown_product_id_count": unknown_product_id_count,
        "unknown_store_id_count": unknown_store_id_count,
        "errors": errors,
        "passed": not errors,
    }


def write_validation_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Write the validation report as readable JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
