# Data Dictionary

## Staging

### `staging_products`

| Column | Meaning |
| --- | --- |
| `product_id` | Product identifier |
| `product_name` | Product display name |
| `category` | Product category |
| `unit_sale_price_ks` | Selling price per unit in Myanmar kyat |
| `unit_cost_ks` | Cost per unit in Myanmar kyat |

### `staging_stores`

| Column | Meaning |
| --- | --- |
| `store_id` | Store identifier |
| `store_name` | Store display name |
| `store_city` | City where the store is located |

### `staging_sales`

| Column | Meaning |
| --- | --- |
| `sale_id` | Unique line-level sale identifier |
| `sale_date` | Date of sale |
| `store_id` | Store identifier |
| `product_id` | Product identifier |
| `units_sold` | Units sold; must be greater than 0 |
| `unit_sale_price_ks` | Selling price per unit |
| `unit_cost_ks` | Cost per unit |
| `revenue_ks` | `units_sold * unit_sale_price_ks` |
| `profit_ks` | `units_sold * (unit_sale_price_ks - unit_cost_ks)` |
| `payment_method` | Payment method used for the sale |

## Warehouse

`dim_products`, `dim_stores`, and `dim_dates` describe the business entities used for analysis.

`fact_sales` stores measurable sales events and joins to dimensions with `product_key`, `store_key`, and `date_key`.

## Marts

`mart_daily_revenue` summarizes revenue and profit by day.

`mart_top_products` ranks products by revenue.

`mart_category_profit` summarizes revenue and profit by category.
