"""Transform raw retail sales rows into clean staging tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


STAGING_SALES_COLUMNS = [
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

STAGING_PRODUCT_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "unit_sale_price_ks",
    "unit_cost_ks",
]

STAGING_STORE_COLUMNS = ["store_id", "store_name", "store_city"]


def combine_raw_frames(raw_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Combine raw files and keep the source filename for reporting."""
    frames: list[pd.DataFrame] = []
    for file_name, df in raw_frames.items():
        with_source = df.copy()
        with_source["source_file"] = file_name
        frames.append(with_source)
    return pd.concat(frames, ignore_index=True)


def standardize_sales_columns(raw_sales: pd.DataFrame) -> pd.DataFrame:
    """Convert supported raw formats into the project staging column names.

    The original project used order-line fields such as ``order_id``,
    ``quantity``, and ``unit_price``. Newer generated files use ``sale_id``,
    ``units_sold``, and ``unit_sale_price_ks`` directly. Supporting both keeps
    the learning project compatible with existing sample data.
    """
    df = raw_sales.copy()
    _strip_whitespace(df)

    if "sale_id" not in df.columns:
        if {"order_id", "product_id"}.issubset(df.columns):
            df["sale_id"] = df["order_id"].astype("string") + "-" + df["product_id"].astype("string")
        else:
            raise ValueError("Raw sales data must contain sale_id or order_id plus product_id.")

    column_aliases = {
        "sale_date": "order_date",
        "units_sold": "quantity",
        "unit_sale_price_ks": "unit_price",
        "category": "category_name",
    }
    for target, source in column_aliases.items():
        if target not in df.columns and source in df.columns:
            df[target] = df[source]

    if "unit_cost_ks" not in df.columns:
        # Existing sample raw files do not include product cost. Use a simple
        # default margin so profit marts remain explainable for learners.
        df["unit_cost_ks"] = pd.to_numeric(df["unit_sale_price_ks"], errors="coerce") * 0.7

    return df


def build_staging_products(raw_sales: pd.DataFrame) -> pd.DataFrame:
    """Build one clean product row per product from standardized raw sales."""
    df = standardize_sales_columns(raw_sales)
    required = ["product_id", "product_name", "category", "unit_sale_price_ks", "unit_cost_ks"]
    _require_columns(df, required, "products")

    products = df[required].copy()
    _strip_whitespace(products)
    products["unit_sale_price_ks"] = _to_number(products["unit_sale_price_ks"])
    products["unit_cost_ks"] = _to_number(products["unit_cost_ks"])

    return (
        products.sort_values(["product_id"])
        .drop_duplicates(subset=["product_id"], keep="last")
        .reset_index(drop=True)
    )


def build_staging_stores(raw_sales: pd.DataFrame) -> pd.DataFrame:
    """Build one clean store row per store from standardized raw sales."""
    df = standardize_sales_columns(raw_sales)
    required = ["store_id", "store_name", "store_city"]
    _require_columns(df, required, "stores")

    stores = df[required].copy()
    _strip_whitespace(stores)
    return (
        stores.sort_values(["store_id"])
        .drop_duplicates(subset=["store_id"], keep="last")
        .reset_index(drop=True)
    )


def build_staging_sales(raw_sales: pd.DataFrame) -> pd.DataFrame:
    """Build clean line-level sales rows with revenue and profit metrics."""
    df = standardize_sales_columns(raw_sales)
    required = [
        "sale_id",
        "sale_date",
        "store_id",
        "product_id",
        "units_sold",
        "unit_sale_price_ks",
        "unit_cost_ks",
        "payment_method",
    ]
    _require_columns(df, required, "sales")

    sales = df[required].copy()
    _strip_whitespace(sales)
    sales["sale_date"] = pd.to_datetime(sales["sale_date"], errors="coerce").dt.date
    sales["units_sold"] = _to_number(sales["units_sold"]).astype("Int64")
    sales["unit_sale_price_ks"] = _to_number(sales["unit_sale_price_ks"])
    sales["unit_cost_ks"] = _to_number(sales["unit_cost_ks"])
    sales["revenue_ks"] = sales["units_sold"] * sales["unit_sale_price_ks"]
    sales["profit_ks"] = sales["units_sold"] * (sales["unit_sale_price_ks"] - sales["unit_cost_ks"])

    return sales.sort_values(["sale_date", "sale_id"]).reset_index(drop=True)


def write_dataframe(df: pd.DataFrame, output_path: str | Path) -> None:
    """Write a DataFrame to CSV, creating parent directories when needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _strip_whitespace(df: pd.DataFrame) -> None:
    """Trim whitespace from text columns in place."""
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].astype("string").str.strip()


def _to_number(series: pd.Series) -> pd.Series:
    """Cast a pandas Series to numeric values."""
    return pd.to_numeric(series, errors="coerce")


def _require_columns(df: pd.DataFrame, required_columns: list[str], label: str) -> None:
    """Raise a helpful error if a required staging input column is missing."""
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required {label} columns: {missing}")
