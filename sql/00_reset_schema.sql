-- Reset local practice tables before reloading the refactored project schema.
-- Use only for a learning database where it is safe to delete prior project tables.

DROP TABLE IF EXISTS
    mart_category_profit,
    mart_top_products,
    mart_daily_revenue,
    fact_sales,
    dim_dates,
    dim_stores,
    dim_products,
    sales,
    order_items,
    orders,
    customers,
    products,
    categories,
    suppliers,
    stores
CASCADE;
