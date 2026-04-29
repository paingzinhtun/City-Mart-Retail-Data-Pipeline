-- Example analytics queries for the City Mart Retail Data Pipeline.

-- 1. Daily revenue and number of orders
SELECT
    d.full_date,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.line_total) AS revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;

-- 2. Revenue by store
SELECT
    s.store_name,
    s.city,
    SUM(f.line_total) AS revenue
FROM fact_sales f
JOIN dim_store s ON f.store_key = s.store_key
GROUP BY s.store_name, s.city
ORDER BY revenue DESC;

-- 3. Top products by revenue
SELECT
    p.product_name,
    p.category_name,
    p.supplier_name,
    SUM(f.quantity) AS units_sold,
    SUM(f.line_total) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_name, p.category_name, p.supplier_name
ORDER BY revenue DESC
LIMIT 10;

-- 4. Customer spend
SELECT
    c.customer_name,
    c.email,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.line_total) AS total_spend
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_name, c.email
ORDER BY total_spend DESC;
