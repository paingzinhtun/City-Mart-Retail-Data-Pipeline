-- Business mart tables created from the warehouse layer.

CREATE TABLE IF NOT EXISTS mart_daily_revenue (
    full_date DATE PRIMARY KEY,
    total_units_sold INTEGER NOT NULL CHECK (total_units_sold >= 0),
    total_revenue_ks NUMERIC(16, 2) NOT NULL CHECK (total_revenue_ks >= 0),
    total_profit_ks NUMERIC(16, 2) NOT NULL,
    transaction_count INTEGER NOT NULL CHECK (transaction_count >= 0)
);

CREATE TABLE IF NOT EXISTS mart_top_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_rank INTEGER NOT NULL CHECK (product_rank > 0),
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(120) NOT NULL,
    total_units_sold INTEGER NOT NULL CHECK (total_units_sold >= 0),
    total_revenue_ks NUMERIC(16, 2) NOT NULL CHECK (total_revenue_ks >= 0),
    total_profit_ks NUMERIC(16, 2) NOT NULL,
    transaction_count INTEGER NOT NULL CHECK (transaction_count >= 0)
);

CREATE TABLE IF NOT EXISTS mart_category_profit (
    category VARCHAR(120) PRIMARY KEY,
    total_units_sold INTEGER NOT NULL CHECK (total_units_sold >= 0),
    total_revenue_ks NUMERIC(16, 2) NOT NULL CHECK (total_revenue_ks >= 0),
    total_profit_ks NUMERIC(16, 2) NOT NULL
);
