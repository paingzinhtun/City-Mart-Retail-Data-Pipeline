"""Clean a simple City Mall-style product catalog snapshot CSV.

This helper is intentionally small. It is useful if you collect a product
catalog CSV separately and want consistent product names, categories, and prices
before using it as reference data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def clean_catalog(input_path: str | Path, output_path: str | Path) -> None:
    """Clean whitespace, remove duplicate products, and normalize prices."""
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Catalog snapshot not found: {source}")

    df = pd.read_csv(source)
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].astype("string").str.strip()

    if "unit_sale_price_ks" in df.columns:
        df["unit_sale_price_ks"] = pd.to_numeric(df["unit_sale_price_ks"], errors="coerce")
    if "unit_cost_ks" in df.columns:
        df["unit_cost_ks"] = pd.to_numeric(df["unit_cost_ks"], errors="coerce")
    if "product_id" in df.columns:
        df = df.drop_duplicates(subset=["product_id"], keep="last")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Clean a product catalog snapshot CSV.")
    parser.add_argument("--input", required=True, help="Input catalog CSV path.")
    parser.add_argument("--output", required=True, help="Cleaned catalog CSV path.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    clean_catalog(args.input, args.output)
    print(f"Wrote cleaned catalog to {args.output}")
