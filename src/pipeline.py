"""Orchestrate the full City Mart CSV-to-marts learning pipeline."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extract import read_raw_sales_files
from marts import build_mart_tables
from transform import (
    build_staging_products,
    build_staging_sales,
    build_staging_stores,
    combine_raw_frames,
    write_dataframe,
)
from validate import build_validation_report, write_validation_report
from warehouse import build_warehouse_tables


RAW_DIR = PROJECT_ROOT / "data" / "raw"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
MARTS_DIR = PROJECT_ROOT / "data" / "marts"


def run_pipeline(
    raw_dir: str | Path = RAW_DIR,
    load_postgres: bool = False,
    reset_postgres: bool = False,
) -> None:
    """Run extract, transform, validation, warehouse, mart, and optional DB load."""
    logger = logging.getLogger(__name__)
    raw_path = Path(raw_dir)
    if reset_postgres and not load_postgres:
        raise ValueError("--reset-postgres requires --load-postgres.")

    try:
        logger.info("Starting pipeline from raw directory: %s", raw_path)
        raw_frames = read_raw_sales_files(raw_path)
        raw_sales = combine_raw_frames(raw_frames)
        logger.info("Extracted %s raw rows from %s file(s).", len(raw_sales), len(raw_frames))

        staging_tables = {
            "staging_products": build_staging_products(raw_sales),
            "staging_stores": build_staging_stores(raw_sales),
            "staging_sales": build_staging_sales(raw_sales),
        }
        _write_tables(staging_tables, STAGING_DIR)
        logger.info("Wrote staging CSV outputs to %s.", STAGING_DIR)

        validation_report = build_validation_report(
            raw_frames,
            staging_tables["staging_products"],
            staging_tables["staging_stores"],
            staging_tables["staging_sales"],
        )
        write_validation_report(validation_report, MARTS_DIR / "validation_report.json")
        if not validation_report["passed"]:
            raise ValueError(f"Validation failed. See {MARTS_DIR / 'validation_report.json'}")
        logger.info("Validation passed. Report written to data/marts/validation_report.json.")

        warehouse_tables = build_warehouse_tables(
            staging_tables["staging_products"],
            staging_tables["staging_stores"],
            staging_tables["staging_sales"],
        )
        _write_tables(warehouse_tables, WAREHOUSE_DIR)
        logger.info("Wrote warehouse CSV outputs to %s.", WAREHOUSE_DIR)

        mart_tables = build_mart_tables(warehouse_tables)
        _write_tables(mart_tables, MARTS_DIR)
        logger.info("Wrote mart CSV outputs to %s.", MARTS_DIR)

        if load_postgres:
            if reset_postgres:
                logger.warning("Resetting PostgreSQL project tables before load.")
            logger.info("Loading staging, warehouse, and mart tables into PostgreSQL.")
            from load import load_pipeline_outputs

            load_pipeline_outputs(
                staging_tables,
                warehouse_tables,
                mart_tables,
                reset_postgres=reset_postgres,
            )
            logger.info("PostgreSQL load completed.")

        logger.info("Pipeline completed successfully.")
    except Exception:
        logger.exception("Pipeline failed.")
        raise


def configure_logging() -> None:
    """Configure readable command-line logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse pipeline command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the City Mart retail ETL pipeline.")
    parser.add_argument(
        "--raw-dir",
        default=str(RAW_DIR),
        help="Directory containing raw daily sales CSV files.",
    )
    parser.add_argument(
        "--load-postgres",
        action="store_true",
        help="Also create/load PostgreSQL tables using config from .env.",
    )
    parser.add_argument(
        "--reset-postgres",
        action="store_true",
        help="Drop prior local project tables before PostgreSQL load. Use only in a practice database.",
    )
    return parser.parse_args()


def _write_tables(tables: dict[str, object], output_dir: Path) -> None:
    """Write named DataFrames as CSV files."""
    for table_name, df in tables.items():
        write_dataframe(df, output_dir / f"{table_name}.csv")


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    run_pipeline(
        raw_dir=args.raw_dir,
        load_postgres=args.load_postgres,
        reset_postgres=args.reset_postgres,
    )
