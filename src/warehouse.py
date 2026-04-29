"""Warehouse layer for populating OLAP star schema tables."""

from pathlib import Path

from load import execute_sql_file, get_connection


def create_olap_schema(sql_file_path: str | Path = "sql/olap_schema.sql") -> None:
    """Create OLAP tables if they do not already exist.

    Args:
        sql_file_path: Path to the OLAP schema SQL file.
    """
    execute_sql_file(sql_file_path)


def populate_warehouse() -> None:
    """Populate OLAP dimensions and fact table from OLTP tables."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            _populate_dim_customer(cursor)
            _populate_dim_store(cursor)
            _populate_dim_product(cursor)
            _populate_dim_date(cursor)
            _populate_fact_sales(cursor)


def _populate_dim_customer(cursor) -> None:
    """Upsert customer dimension records from OLTP customers."""
    cursor.execute(
        """
        INSERT INTO dim_customer (customer_id, customer_name, email, phone)
        SELECT customer_id, customer_name, email, phone
        FROM customers
        ON CONFLICT (customer_id) DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone;
        """
    )


def _populate_dim_store(cursor) -> None:
    """Upsert store dimension records from OLTP stores."""
    cursor.execute(
        """
        INSERT INTO dim_store (store_id, store_name, city)
        SELECT store_id, store_name, city
        FROM stores
        ON CONFLICT (store_id) DO UPDATE SET
            store_name = EXCLUDED.store_name,
            city = EXCLUDED.city;
        """
    )


def _populate_dim_product(cursor) -> None:
    """Upsert denormalized product dimension records from OLTP product tables."""
    cursor.execute(
        """
        INSERT INTO dim_product (product_id, product_name, category_name, supplier_name)
        SELECT
            p.product_id,
            p.product_name,
            c.category_name,
            s.supplier_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category_name = EXCLUDED.category_name,
            supplier_name = EXCLUDED.supplier_name;
        """
    )


def _populate_dim_date(cursor) -> None:
    """Upsert date dimension records for every order date in OLTP orders."""
    cursor.execute(
        """
        INSERT INTO dim_date (
            date_key,
            full_date,
            day,
            month,
            month_name,
            quarter,
            year,
            day_of_week
        )
        SELECT DISTINCT
            TO_CHAR(order_date, 'YYYYMMDD')::INTEGER AS date_key,
            order_date AS full_date,
            EXTRACT(DAY FROM order_date)::INTEGER AS day,
            EXTRACT(MONTH FROM order_date)::INTEGER AS month,
            TO_CHAR(order_date, 'Month') AS month_name,
            EXTRACT(QUARTER FROM order_date)::INTEGER AS quarter,
            EXTRACT(YEAR FROM order_date)::INTEGER AS year,
            TO_CHAR(order_date, 'Day') AS day_of_week
        FROM orders
        ON CONFLICT (date_key) DO UPDATE SET
            full_date = EXCLUDED.full_date,
            day = EXCLUDED.day,
            month = EXCLUDED.month,
            month_name = EXCLUDED.month_name,
            quarter = EXCLUDED.quarter,
            year = EXCLUDED.year,
            day_of_week = EXCLUDED.day_of_week;
        """
    )


def _populate_fact_sales(cursor) -> None:
    """Upsert sales facts by joining OLTP transactions to OLAP dimensions."""
    cursor.execute(
        """
        INSERT INTO fact_sales (
            order_id,
            product_key,
            customer_key,
            store_key,
            date_key,
            quantity,
            unit_price,
            line_total,
            payment_method
        )
        SELECT
            o.order_id,
            dp.product_key,
            dc.customer_key,
            ds.store_key,
            dd.date_key,
            oi.quantity,
            oi.unit_price,
            oi.line_total,
            o.payment_method
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN dim_customer dc ON o.customer_id = dc.customer_id
        JOIN dim_store ds ON o.store_id = ds.store_id
        JOIN dim_product dp ON oi.product_id = dp.product_id
        JOIN dim_date dd ON o.order_date = dd.full_date
        ON CONFLICT (order_id, product_key) DO UPDATE SET
            customer_key = EXCLUDED.customer_key,
            store_key = EXCLUDED.store_key,
            date_key = EXCLUDED.date_key,
            quantity = EXCLUDED.quantity,
            unit_price = EXCLUDED.unit_price,
            line_total = EXCLUDED.line_total,
            payment_method = EXCLUDED.payment_method,
            loaded_at = CURRENT_TIMESTAMP;
        """
    )
