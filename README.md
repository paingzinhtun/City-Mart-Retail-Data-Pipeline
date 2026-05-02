# City Mart-Style Retail Data Engineering Pipeline

Production-minded, beginner-friendly retail data pipeline built with Python, pandas, PostgreSQL, and SQL data modeling fundamentals.

This project simulates how a retail company can process daily store sales files, validate data quality, model sales into a warehouse star schema, and publish business-ready marts for analytics.

> This project uses simulated Myanmar retail data for learning and portfolio purposes. It is not official City Mart data.

## Project Summary

Retail businesses often receive daily sales data as CSV files from stores or systems. Raw files are not ideal for analytics because they may contain inconsistent column names, text spacing issues, invalid numeric values, duplicate records, or missing reference data.

This project demonstrates a practical data engineering workflow:

```text
Raw CSV
-> Python ETL modules
-> Data validation report
-> Staging data
-> PostgreSQL tables
-> Warehouse star schema
-> Business marts
-> Analytics queries
```

The project intentionally avoids Airflow, Spark, Docker, and cloud services for now so the core fundamentals stay clear: Python, SQL, PostgreSQL, validation, ETL, and dimensional modeling.

## What This Project Demonstrates

- Batch data ingestion from raw CSV files
- Modular Python ETL design
- Data cleaning and type casting with pandas
- Data quality validation with a JSON report
- PostgreSQL loading with environment-based credentials
- Primary keys, foreign keys, `NOT NULL`, `CHECK`, and upsert logic
- Warehouse modeling with dimensions and facts
- Business marts for reporting and analytics
- Clear project documentation for a data engineering portfolio

## Business Questions Answered

The final marts and SQL queries help answer:

- How much revenue did the business make each day?
- Which products generated the most revenue?
- Which categories generated the most profit?
- Which stores and products performed best?

## Architecture

```text
data/raw/*.csv
    |
    v
src/extract.py
    |
    v
src/transform.py
    |
    v
src/validate.py  --->  data/marts/validation_report.json
    |
    v
data/staging/*.csv
    |
    v
src/warehouse.py
    |
    v
data/warehouse/*.csv
    |
    v
src/marts.py
    |
    v
data/marts/*.csv
    |
    v
src/load.py  --->  PostgreSQL tables
```

## Core Business Logic

The pipeline keeps the business logic simple and transparent:

```text
revenue_ks = units_sold * unit_sale_price_ks
profit_ks = units_sold * (unit_sale_price_ks - unit_cost_ks)
```

The included older raw CSV files do not contain cost, so the transform layer estimates `unit_cost_ks` as 70% of the sale price. New generated raw files include `unit_cost_ks` directly.

## Repository Structure

```text
city_mart_retail_pipeline/
|-- config/
|   |-- db_config.py
|-- data/
|   |-- raw/
|   |-- staging/
|   |-- warehouse/
|   |-- marts/
|-- docs/
|   |-- fundamentals.md
|   |-- data_dictionary.md
|   |-- project_guide.md
|-- scripts/
|   |-- generate_raw_sales.py
|   |-- clean_citymall_catalog_snapshot.py
|-- src/
|   |-- __init__.py
|   |-- extract.py
|   |-- transform.py
|   |-- validate.py
|   |-- load.py
|   |-- warehouse.py
|   |-- marts.py
|   |-- pipeline.py
|-- sql/
|   |-- 00_reset_schema.sql
|   |-- 01_oltp_schema.sql
|   |-- 02_warehouse_schema.sql
|   |-- 03_marts.sql
|   |-- 04_analysis_queries.sql
|-- .env.example
|-- requirements.txt
|-- README.md
```

## Data Layers

### Raw

Location: [data/raw](data/raw)

Raw daily sales CSV files. This layer represents source data before engineering cleanup.

### Staging

Location: [data/staging](data/staging)

Cleaned, typed, standardized CSV outputs:

- `staging_products.csv`
- `staging_stores.csv`
- `staging_sales.csv`

### Warehouse

Location: [data/warehouse](data/warehouse)

Star schema outputs:

- `dim_products.csv`
- `dim_stores.csv`
- `dim_dates.csv`
- `fact_sales.csv`

### Marts

Location: [data/marts](data/marts)

Business-ready reporting outputs:

- `mart_daily_revenue.csv`
- `mart_top_products.csv`
- `mart_category_profit.csv`
- `validation_report.json`

## Python Modules

| Module | Responsibility |
| --- | --- |
| [src/extract.py](src/extract.py) | Read raw CSV files and check file availability |
| [src/transform.py](src/transform.py) | Clean columns, cast types, create staging tables |
| [src/validate.py](src/validate.py) | Run data quality checks and build validation report |
| [src/warehouse.py](src/warehouse.py) | Build dimensions and fact table |
| [src/marts.py](src/marts.py) | Build business summary tables |
| [src/load.py](src/load.py) | Load data into PostgreSQL with transactions and upserts |
| [src/pipeline.py](src/pipeline.py) | Orchestrate the full pipeline |

## SQL Files

| File | Purpose |
| --- | --- |
| [sql/00_reset_schema.sql](sql/00_reset_schema.sql) | Drops local practice tables before a clean reload |
| [sql/01_oltp_schema.sql](sql/01_oltp_schema.sql) | Creates cleaned operational tables |
| [sql/02_warehouse_schema.sql](sql/02_warehouse_schema.sql) | Creates warehouse dimension and fact tables |
| [sql/03_marts.sql](sql/03_marts.sql) | Creates business mart tables |
| [sql/04_analysis_queries.sql](sql/04_analysis_queries.sql) | Example analytics queries |

## Quick Start

### 1. Create Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run The CSV Pipeline

```powershell
python src/pipeline.py
```

Expected result:

```text
Extracted raw rows
Wrote staging CSV outputs
Validation passed
Wrote warehouse CSV outputs
Wrote mart CSV outputs
Pipeline completed successfully
```

### 3. Review Outputs

```powershell
Get-Content data\marts\validation_report.json
Get-Content data\marts\mart_daily_revenue.csv
Get-Content data\marts\mart_top_products.csv -TotalCount 10
Get-Content data\marts\mart_category_profit.csv
```

## PostgreSQL Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE city_mart;
```

Create a local `.env` file from [.env.example](.env.example):

```powershell
copy .env.example .env
```

Edit `.env` with your local database credentials:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=city_mart
DB_USER=postgres
DB_PASSWORD=your_password
```

Run the pipeline and load PostgreSQL:

```powershell
python src/pipeline.py --load-postgres
```

For a local practice database where it is safe to remove old project tables:

```powershell
python src/pipeline.py --load-postgres --reset-postgres
```

The loader uses transactions. If the load fails, the transaction rolls back instead of leaving a partial load.

## PostgreSQL Verification

Run these queries after loading:

```sql
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM stores;
SELECT COUNT(*) FROM sales;
SELECT COUNT(*) FROM dim_products;
SELECT COUNT(*) FROM dim_stores;
SELECT COUNT(*) FROM dim_dates;
SELECT COUNT(*) FROM fact_sales;
SELECT COUNT(*) FROM mart_daily_revenue;
SELECT COUNT(*) FROM mart_top_products;
SELECT COUNT(*) FROM mart_category_profit;
```

Expected key counts for the included sample data:

```text
products: 27
stores: 6
sales: 33
dim_dates: 4
fact_sales: 33
```

Business checks:

```sql
SELECT * FROM mart_daily_revenue ORDER BY full_date;
SELECT * FROM mart_top_products ORDER BY product_rank LIMIT 10;
SELECT * FROM mart_category_profit ORDER BY total_profit_ks DESC;
```

## Data Validation

Every pipeline run creates:

[data/marts/validation_report.json](data/marts/validation_report.json)

The report includes:

- Raw row counts
- Staging row counts
- Duplicate `sale_id` count
- Missing value counts per file
- Invalid price count
- Invalid unit count
- Unknown `product_id` count
- Unknown `store_id` count
- Overall pass/fail status

Validation is important because analytics should not be built on silent data quality failures.

## Generate More Sample Data

Generate a new raw daily sales file:

```powershell
python scripts/generate_raw_sales.py
```

Generate a specific date and row count:

```powershell
python scripts/generate_raw_sales.py --date 2026-05-02 --rows 50
```

Then rerun:

```powershell
python src/pipeline.py
```

## Documentation

More project documentation:

- [docs/project_guide.md](docs/project_guide.md): Full explanation of the project, flow, and real-world value
- [docs/fundamentals.md](docs/fundamentals.md): Core data engineering concepts used here
- [docs/data_dictionary.md](docs/data_dictionary.md): Column definitions for staging, warehouse, and marts

## Real-World Value

In a real retail company, a pipeline like this can support:

- Daily sales reporting
- Product performance monitoring
- Store performance analysis
- Category profitability tracking
- Data quality checks before dashboards
- Better decision-making for operations, merchandising, and finance teams

The same pattern can be extended to larger systems with scheduling, orchestration, cloud storage, and BI dashboards.

## Current Scope

Included:

- Python ETL
- CSV source and output layers
- JSON validation report
- PostgreSQL schemas and loading
- Warehouse star schema
- Business marts
- SQL analysis examples

Not included yet:

- Airflow orchestration
- Docker setup
- Cloud deployment
- Spark processing
- BI dashboard

Those are good future improvements after the fundamentals are solid.

## Portfolio Notes

This project is designed to show that you understand the core data engineering lifecycle:

```text
Ingest -> Clean -> Validate -> Model -> Load -> Serve analytics
```

It is small enough to explain in an interview, but complete enough to demonstrate practical engineering habits: modular code, data quality checks, SQL constraints, dimensional modeling, and clear documentation.
