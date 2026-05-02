-- OLTP-style cleaned tables for the City Mart learning project.

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(120) NOT NULL,
    unit_sale_price_ks NUMERIC(14, 2) NOT NULL CHECK (unit_sale_price_ks >= 0),
    unit_cost_ks NUMERIC(14, 2) NOT NULL CHECK (unit_cost_ks >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    store_city VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR(100) PRIMARY KEY,
    sale_date DATE NOT NULL,
    store_id VARCHAR(50) NOT NULL REFERENCES stores(store_id),
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    units_sold INTEGER NOT NULL CHECK (units_sold > 0),
    unit_sale_price_ks NUMERIC(14, 2) NOT NULL CHECK (unit_sale_price_ks >= 0),
    unit_cost_ks NUMERIC(14, 2) NOT NULL CHECK (unit_cost_ks >= 0),
    revenue_ks NUMERIC(16, 2) NOT NULL CHECK (revenue_ks >= 0),
    profit_ks NUMERIC(16, 2) NOT NULL,
    payment_method VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_store_id ON sales(store_id);
