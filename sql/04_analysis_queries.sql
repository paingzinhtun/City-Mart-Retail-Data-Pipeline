-- Example business questions answered from the mart and warehouse tables.

-- 1. Daily revenue and profit
SELECT
    full_date,
    transaction_count,
    total_units_sold,
    total_revenue_ks,
    total_profit_ks
FROM mart_daily_revenue
ORDER BY full_date;

-- 2. Top products by revenue
SELECT
    product_rank,
    product_name,
    category,
    total_units_sold,
    total_revenue_ks,
    total_profit_ks
FROM mart_top_products
ORDER BY product_rank
LIMIT 10;

-- 3. Profit by category
SELECT
    category,
    total_units_sold,
    total_revenue_ks,
    total_profit_ks
FROM mart_category_profit
ORDER BY total_profit_ks DESC;

-- 4. Store and product sales performance
SELECT
    ds.store_name,
    ds.store_city,
    dp.product_name,
    dp.category,
    SUM(fs.units_sold) AS total_units_sold,
    SUM(fs.revenue_ks) AS total_revenue_ks,
    SUM(fs.profit_ks) AS total_profit_ks
FROM fact_sales fs
JOIN dim_stores ds ON fs.store_key = ds.store_key
JOIN dim_products dp ON fs.product_key = dp.product_key
GROUP BY ds.store_name, ds.store_city, dp.product_name, dp.category
ORDER BY total_revenue_ks DESC;
