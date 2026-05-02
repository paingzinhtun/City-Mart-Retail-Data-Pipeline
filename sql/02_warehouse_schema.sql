-- Warehouse star schema for analytics.

CREATE TABLE IF NOT EXISTS dim_products (
    product_key INTEGER PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_stores (
    store_key INTEGER PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL UNIQUE,
    store_name VARCHAR(255) NOT NULL,
    store_city VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_dates (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER NOT NULL,
    day_of_week VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id VARCHAR(100) PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_dates(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_products(product_key),
    store_key INTEGER NOT NULL REFERENCES dim_stores(store_key),
    units_sold INTEGER NOT NULL CHECK (units_sold > 0),
    unit_sale_price_ks NUMERIC(14, 2) NOT NULL CHECK (unit_sale_price_ks >= 0),
    unit_cost_ks NUMERIC(14, 2) NOT NULL CHECK (unit_cost_ks >= 0),
    revenue_ks NUMERIC(16, 2) NOT NULL CHECK (revenue_ks >= 0),
    profit_ks NUMERIC(16, 2) NOT NULL,
    payment_method VARCHAR(100),
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key ON fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_store_key ON fact_sales(store_key);
