"""Load layer for inserting transformed sales data into OLTP tables."""

from pathlib import Path
from typing import Iterable

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from config.db_config import DB_CONFIG


def get_connection():
    """Create and return a PostgreSQL connection using project configuration."""
    return psycopg2.connect(**DB_CONFIG)


def execute_sql_file(sql_file_path: str | Path) -> None:
    """Execute every SQL statement from a schema file.

    Args:
        sql_file_path: Path to a SQL file.
    """
    sql_path = Path(sql_file_path)
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_path.read_text(encoding="utf-8"))


def _unique_records(
    df: pd.DataFrame,
    columns: list[str],
    conflict_columns: list[str] | None = None,
) -> list[tuple]:
    """Return unique tuples for a set of columns using conflict keys when provided."""
    subset = conflict_columns or columns
    unique_df = df[columns].drop_duplicates(subset=subset, keep="last")
    return list(unique_df.itertuples(index=False, name=None))


def _upsert_records(query: str, records: Iterable[tuple]) -> None:
    """Run a bulk UPSERT statement if records are available."""
    records = list(records)
    if not records:
        return

    with get_connection() as conn:
        with conn.cursor() as cursor:
            execute_values(cursor, query, records)


def load_to_oltp(df: pd.DataFrame) -> None:
    """Load transformed sales data into normalized OLTP tables.

    Args:
        df: Transformed sales DataFrame.
    """
    load_customers(df)
    load_stores(df)
    load_suppliers(df)
    load_categories(df)
    load_products(df)
    load_orders(df)
    load_order_items(df)


def load_customers(df: pd.DataFrame) -> None:
    """Upsert customer records into the customers table."""
    records = _unique_records(
        df,
        ["customer_id", "customer_name", "customer_email", "customer_phone"],
        ["customer_id"],
    )
    query = """
        INSERT INTO customers (customer_id, customer_name, email, phone)
        VALUES %s
        ON CONFLICT (customer_id) DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)


def load_stores(df: pd.DataFrame) -> None:
    """Upsert store records into the stores table."""
    records = _unique_records(df, ["store_id", "store_name", "store_city"], ["store_id"])
    query = """
        INSERT INTO stores (store_id, store_name, city)
        VALUES %s
        ON CONFLICT (store_id) DO UPDATE SET
            store_name = EXCLUDED.store_name,
            city = EXCLUDED.city,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)


def load_suppliers(df: pd.DataFrame) -> None:
    """Upsert supplier records into the suppliers table."""
    records = _unique_records(df, ["supplier_id", "supplier_name"], ["supplier_id"])
    query = """
        INSERT INTO suppliers (supplier_id, supplier_name)
        VALUES %s
        ON CONFLICT (supplier_id) DO UPDATE SET
            supplier_name = EXCLUDED.supplier_name,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)


def load_categories(df: pd.DataFrame) -> None:
    """Upsert category records into the categories table."""
    records = _unique_records(df, ["category_id", "category_name"], ["category_id"])
    query = """
        INSERT INTO categories (category_id, category_name)
        VALUES %s
        ON CONFLICT (category_id) DO UPDATE SET
            category_name = EXCLUDED.category_name,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)


def load_products(df: pd.DataFrame) -> None:
    """Upsert product records into the products table."""
    records = _unique_records(
        df,
        ["product_id", "product_name", "category_id", "supplier_id", "unit_price"],
        ["product_id"],
    )
    query = """
        INSERT INTO products (product_id, product_name, category_id, supplier_id, unit_price)
        VALUES %s
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category_id = EXCLUDED.category_id,
            supplier_id = EXCLUDED.supplier_id,
            unit_price = EXCLUDED.unit_price,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)


def load_orders(df: pd.DataFrame) -> None:
    """Upsert order header records into the orders table."""
    records = _unique_records(
        df,
        ["order_id", "order_date", "customer_id", "store_id", "payment_method"],
        ["order_id"],
    )
    query = """
        INSERT INTO orders (order_id, order_date, customer_id, store_id, payment_method)
        VALUES %s
        ON CONFLICT (order_id) DO UPDATE SET
            order_date = EXCLUDED.order_date,
            customer_id = EXCLUDED.customer_id,
            store_id = EXCLUDED.store_id,
            payment_method = EXCLUDED.payment_method,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)


def load_order_items(df: pd.DataFrame) -> None:
    """Upsert order line records into the order_items table."""
    records = _unique_records(
        df,
        ["order_id", "product_id", "quantity", "unit_price", "line_total"],
        ["order_id", "product_id"],
    )
    query = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
        VALUES %s
        ON CONFLICT (order_id, product_id) DO UPDATE SET
            quantity = EXCLUDED.quantity,
            unit_price = EXCLUDED.unit_price,
            line_total = EXCLUDED.line_total,
            updated_at = CURRENT_TIMESTAMP;
    """
    _upsert_records(query, records)
