"""PostgreSQL loading helpers for staging, warehouse, and mart tables."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import execute_values

from config.db_config import DB_CONFIG, validate_db_config


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_connection() -> PgConnection:
    """Create a PostgreSQL connection from environment-backed config."""
    validate_db_config()
    return psycopg2.connect(**DB_CONFIG)


def execute_sql_file(cursor, sql_file_path: str | Path) -> None:
    """Execute a SQL file using an existing transaction cursor."""
    path = PROJECT_ROOT / sql_file_path if not Path(sql_file_path).is_absolute() else Path(sql_file_path)
    cursor.execute(path.read_text(encoding="utf-8"))


def load_pipeline_outputs(
    staging_tables: dict[str, pd.DataFrame],
    warehouse_tables: dict[str, pd.DataFrame],
    mart_tables: dict[str, pd.DataFrame],
    reset_postgres: bool = False,
) -> None:
    """Load all project outputs into PostgreSQL in one transaction."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                if reset_postgres:
                    execute_sql_file(cursor, "sql/00_reset_schema.sql")
                execute_sql_file(cursor, "sql/01_oltp_schema.sql")
                execute_sql_file(cursor, "sql/02_warehouse_schema.sql")
                execute_sql_file(cursor, "sql/03_marts.sql")

                _load_products(cursor, staging_tables["staging_products"])
                _load_stores(cursor, staging_tables["staging_stores"])
                _load_sales(cursor, staging_tables["staging_sales"])

                _load_dim_products(cursor, warehouse_tables["dim_products"])
                _load_dim_stores(cursor, warehouse_tables["dim_stores"])
                _load_dim_dates(cursor, warehouse_tables["dim_dates"])
                _load_fact_sales(cursor, warehouse_tables["fact_sales"])

                _load_mart_daily_revenue(cursor, mart_tables["mart_daily_revenue"])
                _load_mart_top_products(cursor, mart_tables["mart_top_products"])
                _load_mart_category_profit(cursor, mart_tables["mart_category_profit"])
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _records(df: pd.DataFrame, columns: list[str]) -> list[tuple]:
    """Return tuples with pandas missing values converted to ``None``."""
    return [
        tuple(_to_python_value(value) for value in row)
        for row in df[columns].itertuples(index=False, name=None)
    ]


def _to_python_value(value):
    """Convert pandas and NumPy scalar values into psycopg2-friendly values."""
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if hasattr(value, "item"):
        return value.item()
    return value


def _execute_values(cursor, query: str, records: Iterable[tuple]) -> None:
    """Run a bulk insert/upsert when records are present."""
    rows = list(records)
    if rows:
        execute_values(cursor, query, rows)


def _load_products(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO products (product_id, product_name, category, unit_sale_price_ks, unit_cost_ks)
        VALUES %s
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            unit_sale_price_ks = EXCLUDED.unit_sale_price_ks,
            unit_cost_ks = EXCLUDED.unit_cost_ks,
            updated_at = CURRENT_TIMESTAMP;
    """
    _execute_values(cursor, query, _records(df, ["product_id", "product_name", "category", "unit_sale_price_ks", "unit_cost_ks"]))


def _load_stores(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO stores (store_id, store_name, store_city)
        VALUES %s
        ON CONFLICT (store_id) DO UPDATE SET
            store_name = EXCLUDED.store_name,
            store_city = EXCLUDED.store_city,
            updated_at = CURRENT_TIMESTAMP;
    """
    _execute_values(cursor, query, _records(df, ["store_id", "store_name", "store_city"]))


def _load_sales(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO sales (
            sale_id, sale_date, store_id, product_id, units_sold,
            unit_sale_price_ks, unit_cost_ks, revenue_ks, profit_ks, payment_method
        )
        VALUES %s
        ON CONFLICT (sale_id) DO UPDATE SET
            sale_date = EXCLUDED.sale_date,
            store_id = EXCLUDED.store_id,
            product_id = EXCLUDED.product_id,
            units_sold = EXCLUDED.units_sold,
            unit_sale_price_ks = EXCLUDED.unit_sale_price_ks,
            unit_cost_ks = EXCLUDED.unit_cost_ks,
            revenue_ks = EXCLUDED.revenue_ks,
            profit_ks = EXCLUDED.profit_ks,
            payment_method = EXCLUDED.payment_method,
            updated_at = CURRENT_TIMESTAMP;
    """
    _execute_values(cursor, query, _records(df, [
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
    ]))


def _load_dim_products(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO dim_products (product_key, product_id, product_name, category)
        VALUES %s
        ON CONFLICT (product_id) DO UPDATE SET
            product_key = EXCLUDED.product_key,
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category;
    """
    _execute_values(cursor, query, _records(df, ["product_key", "product_id", "product_name", "category"]))


def _load_dim_stores(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO dim_stores (store_key, store_id, store_name, store_city)
        VALUES %s
        ON CONFLICT (store_id) DO UPDATE SET
            store_key = EXCLUDED.store_key,
            store_name = EXCLUDED.store_name,
            store_city = EXCLUDED.store_city;
    """
    _execute_values(cursor, query, _records(df, ["store_key", "store_id", "store_name", "store_city"]))


def _load_dim_dates(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO dim_dates (date_key, full_date, day, month, month_name, quarter, year, day_of_week)
        VALUES %s
        ON CONFLICT (date_key) DO UPDATE SET
            full_date = EXCLUDED.full_date,
            day = EXCLUDED.day,
            month = EXCLUDED.month,
            month_name = EXCLUDED.month_name,
            quarter = EXCLUDED.quarter,
            year = EXCLUDED.year,
            day_of_week = EXCLUDED.day_of_week;
    """
    _execute_values(cursor, query, _records(df, ["date_key", "full_date", "day", "month", "month_name", "quarter", "year", "day_of_week"]))


def _load_fact_sales(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO fact_sales (
            sale_id, date_key, product_key, store_key, units_sold,
            unit_sale_price_ks, unit_cost_ks, revenue_ks, profit_ks, payment_method
        )
        VALUES %s
        ON CONFLICT (sale_id) DO UPDATE SET
            date_key = EXCLUDED.date_key,
            product_key = EXCLUDED.product_key,
            store_key = EXCLUDED.store_key,
            units_sold = EXCLUDED.units_sold,
            unit_sale_price_ks = EXCLUDED.unit_sale_price_ks,
            unit_cost_ks = EXCLUDED.unit_cost_ks,
            revenue_ks = EXCLUDED.revenue_ks,
            profit_ks = EXCLUDED.profit_ks,
            payment_method = EXCLUDED.payment_method,
            updated_at = CURRENT_TIMESTAMP;
    """
    _execute_values(cursor, query, _records(df, [
        "sale_id",
        "date_key",
        "product_key",
        "store_key",
        "units_sold",
        "unit_sale_price_ks",
        "unit_cost_ks",
        "revenue_ks",
        "profit_ks",
        "payment_method",
    ]))


def _load_mart_daily_revenue(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO mart_daily_revenue (
            full_date, total_units_sold, total_revenue_ks, total_profit_ks, transaction_count
        )
        VALUES %s
        ON CONFLICT (full_date) DO UPDATE SET
            total_units_sold = EXCLUDED.total_units_sold,
            total_revenue_ks = EXCLUDED.total_revenue_ks,
            total_profit_ks = EXCLUDED.total_profit_ks,
            transaction_count = EXCLUDED.transaction_count;
    """
    _execute_values(cursor, query, _records(df, ["full_date", "total_units_sold", "total_revenue_ks", "total_profit_ks", "transaction_count"]))


def _load_mart_top_products(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO mart_top_products (
            product_rank, product_id, product_name, category, total_units_sold,
            total_revenue_ks, total_profit_ks, transaction_count
        )
        VALUES %s
        ON CONFLICT (product_id) DO UPDATE SET
            product_rank = EXCLUDED.product_rank,
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            total_units_sold = EXCLUDED.total_units_sold,
            total_revenue_ks = EXCLUDED.total_revenue_ks,
            total_profit_ks = EXCLUDED.total_profit_ks,
            transaction_count = EXCLUDED.transaction_count;
    """
    _execute_values(cursor, query, _records(df, [
        "product_rank",
        "product_id",
        "product_name",
        "category",
        "total_units_sold",
        "total_revenue_ks",
        "total_profit_ks",
        "transaction_count",
    ]))


def _load_mart_category_profit(cursor, df: pd.DataFrame) -> None:
    query = """
        INSERT INTO mart_category_profit (
            category, total_units_sold, total_revenue_ks, total_profit_ks
        )
        VALUES %s
        ON CONFLICT (category) DO UPDATE SET
            total_units_sold = EXCLUDED.total_units_sold,
            total_revenue_ks = EXCLUDED.total_revenue_ks,
            total_profit_ks = EXCLUDED.total_profit_ks;
    """
    _execute_values(cursor, query, _records(df, ["category", "total_units_sold", "total_revenue_ks", "total_profit_ks"]))
