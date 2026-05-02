# Data Engineering Fundamentals

This project demonstrates a small batch data pipeline for retail sales.

## Layers

Raw data is the original CSV input. It should be kept close to the source shape.

Staging data is cleaned and typed. This layer fixes whitespace, dates, numeric values, and business metric columns.

Warehouse data is modeled for analytics. The project uses dimensions and a fact table:

- `dim_products`
- `dim_stores`
- `dim_dates`
- `fact_sales`

Mart data answers common business questions with ready-to-query summary tables:

- `mart_daily_revenue`
- `mart_top_products`
- `mart_category_profit`

## Validation

The pipeline writes `data/marts/validation_report.json` on each run. It reports row counts, missing values, duplicate `sale_id` values, invalid units or prices, and unknown product/store references.

## PostgreSQL

The CSV outputs are useful for learning and review. PostgreSQL support shows how the same cleaned data can be loaded into constrained tables with primary keys, foreign keys, checks, and upserts.
