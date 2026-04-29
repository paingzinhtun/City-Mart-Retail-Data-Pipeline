"""Pipeline runner for City Mart Retail Data Pipeline."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extract import extract_sales_csv
from load import execute_sql_file, load_to_oltp
from transform import save_processed_data, transform_sales_data
from warehouse import create_olap_schema, populate_warehouse


DEFAULT_RAW_FILE = Path("data/raw/daily_sales_2026_04_28.csv")
DEFAULT_PROCESSED_DIR = Path("data/processed")


def run_pipeline(csv_file_path: str | Path) -> None:
    """Run the full batch pipeline from raw CSV to OLAP warehouse.

    Args:
        csv_file_path: Path to a raw sales CSV file.
    """
    csv_path = Path(csv_file_path)
    processed_path = DEFAULT_PROCESSED_DIR / f"{csv_path.stem}_processed.csv"

    try:
        print(f"Starting pipeline for: {csv_path}")

        print("Step 1/6: Extracting CSV data...")
        raw_df = extract_sales_csv(csv_path)
        print(f"Extracted {len(raw_df)} raw rows.")

        print("Step 2/6: Transforming and validating data...")
        transformed_df = transform_sales_data(raw_df)
        save_processed_data(transformed_df, processed_path)
        print(f"Transformed {len(transformed_df)} rows. Saved to {processed_path}.")

        print("Step 3/6: Creating OLTP schema...")
        execute_sql_file("sql/oltp_schema.sql")

        print("Step 4/6: Loading OLTP tables...")
        load_to_oltp(transformed_df)

        print("Step 5/6: Creating OLAP schema...")
        create_olap_schema("sql/olap_schema.sql")

        print("Step 6/6: Populating warehouse star schema...")
        populate_warehouse()

        print("Pipeline completed successfully.")
    except Exception as exc:
        print(f"Pipeline failed: {exc}")
        raise


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the pipeline runner."""
    parser = argparse.ArgumentParser(description="Run the City Mart retail batch pipeline.")
    parser.add_argument(
        "--file",
        default=str(DEFAULT_RAW_FILE),
        help="Path to the raw daily sales CSV file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.file)
