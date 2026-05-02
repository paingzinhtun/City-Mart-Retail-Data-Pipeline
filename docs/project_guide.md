# City Mart-Style Retail Data Pipeline Guide

## What This Project Is About

This project is a beginner-to-intermediate data engineering portfolio project. It simulates how a retail company could process daily sales data from stores and turn it into clean, useful business reporting tables.

The project uses simulated Myanmar retail data. It is inspired by real retail workflows, but it is not official City Mart data.

The main goal is to show the fundamentals of data engineering:

- Reading raw CSV files
- Cleaning and standardizing data with Python
- Validating data quality
- Building staging, warehouse, and mart layers
- Loading structured data into PostgreSQL
- Writing SQL queries for business analysis

## Business Problem

A retail business receives sales data every day. The raw files are useful, but they are not ready for reporting because they may have inconsistent columns, text spacing issues, wrong data types, missing values, duplicate rows, or invalid values.

Business users want answers to questions such as:

- How much revenue did we make each day?
- Which products sold the most?
- Which categories generated the most profit?
- Which stores and products performed best?

A data engineer builds a pipeline that turns raw sales data into reliable reporting tables.

## How The Project Works

The pipeline follows this flow:

```text
Raw CSV
-> Python ETL modules
-> Data validation report
-> Staging tables
-> PostgreSQL tables
-> Warehouse/star schema
-> Business marts
-> Analytics queries
```

## Step 1: Raw CSV Data

Raw data lives in:

```text
data/raw/
```

Each raw CSV file represents daily retail sales. The existing sample files contain fields such as:

- `order_id`
- `order_date`
- `store_id`
- `product_id`
- `product_name`
- `category_name`
- `quantity`
- `unit_price`
- `payment_method`

The pipeline also supports the newer learning schema with:

- `sale_id`
- `sale_date`
- `units_sold`
- `unit_sale_price_ks`
- `unit_cost_ks`

## Step 2: Extract

Code:

```text
src/extract.py
```

The extract layer reads CSV files from `data/raw/`.

It checks that:

- The raw folder exists
- CSV files exist
- Files are not empty

The output is a pandas DataFrame used by the transform layer.

## Step 3: Transform

Code:

```text
src/transform.py
```

The transform layer cleans and standardizes the data.

It performs tasks such as:

- Trimming whitespace from text fields
- Standardizing old raw column names into the new learning schema
- Parsing dates
- Casting numeric columns
- Creating product, store, and sales staging tables
- Calculating revenue and profit

Important formulas:

```text
revenue_ks = units_sold * unit_sale_price_ks
profit_ks = units_sold * (unit_sale_price_ks - unit_cost_ks)
```

The transform output is written to:

```text
data/staging/
```

## Step 4: Validate

Code:

```text
src/validate.py
```

The validation layer checks data quality before warehouse and mart outputs are trusted.

It checks:

- Required columns
- Missing values
- Duplicate `sale_id`
- `units_sold > 0`
- `unit_sale_price_ks >= 0`
- `unit_cost_ks >= 0`
- Unknown `product_id`
- Unknown `store_id`

The validation report is written to:

```text
data/marts/validation_report.json
```

This is useful because real-world pipelines should not silently accept bad data.

## Step 5: Warehouse

Code:

```text
src/warehouse.py
```

The warehouse layer creates a simple star schema.

Dimension tables:

- `dim_products`
- `dim_stores`
- `dim_dates`

Fact table:

- `fact_sales`

The fact table stores measurable business events, such as units sold, revenue, and profit. The dimension tables describe the product, store, and date context.

Warehouse CSV outputs are written to:

```text
data/warehouse/
```

## Step 6: Marts

Code:

```text
src/marts.py
```

Marts are business-friendly summary tables. They are easier for analysts, dashboard tools, and business users to query.

This project creates:

- `mart_daily_revenue`
- `mart_top_products`
- `mart_category_profit`

Mart CSV outputs are written to:

```text
data/marts/
```

## Step 7: PostgreSQL Load

Code:

```text
src/load.py
config/db_config.py
```

The project can load staging, warehouse, and mart tables into PostgreSQL.

Database credentials are read from `.env`, not hardcoded in Python.

Example `.env`:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=city_mart
DB_USER=postgres
DB_PASSWORD=your_password
```

SQL schema files:

```text
sql/01_oltp_schema.sql
sql/02_warehouse_schema.sql
sql/03_marts.sql
sql/04_analysis_queries.sql
```

The database layer uses:

- Primary keys
- Foreign keys
- Not null constraints
- Check constraints
- Upsert logic
- Transaction handling
- Rollback on error

## How To Run The Project

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the CSV pipeline:

```powershell
python src/pipeline.py
```

Run the CSV pipeline and load PostgreSQL:

```powershell
python src/pipeline.py --load-postgres
```

For a local practice database where old project tables can be removed:

```powershell
python src/pipeline.py --load-postgres --reset-postgres
```

Generate an extra raw sales file:

```powershell
python scripts/generate_raw_sales.py
```

## How This Helps In The Real World

This project demonstrates the same thinking used in real data engineering teams, just at a smaller scale.

In real companies, data engineers often:

- Collect raw files from stores, apps, vendors, or APIs
- Clean and standardize inconsistent data
- Validate data before it reaches reports
- Load data into databases
- Design warehouse tables for analytics
- Build marts for dashboards and business users
- Write SQL queries for decision-making

For a retail business, this kind of pipeline can help teams understand:

- Daily revenue trends
- Best-selling products
- High-profit categories
- Store performance
- Product performance
- Data quality issues in source files

## What Skills This Project Shows

This project shows practical skills in:

- Python ETL development
- pandas data cleaning
- Data validation
- PostgreSQL loading
- SQL schema design
- Star schema modeling
- Fact and dimension tables
- Business mart design
- Environment variable configuration
- Beginner-friendly pipeline orchestration

## Why This Is Good For A Portfolio

This project is useful for a data engineering portfolio because it is small enough to understand but complete enough to show real engineering workflow.

It demonstrates that you can move data through a full pipeline:

```text
Raw data -> Clean data -> Validated data -> Warehouse -> Marts -> Business answers
```

That is the core responsibility of many junior and intermediate data engineering roles.

## Future Improvements

Good next improvements are:

- Add unit tests for transform and validation logic
- Add rejected rows output
- Add a PostgreSQL row-count verification script
- Add a dashboard with Power BI, Metabase, or Streamlit
- Add Docker later for easier PostgreSQL setup
- Add Airflow later for scheduled orchestration

The project intentionally avoids Airflow, Spark, cloud services, and Docker at this stage so the fundamentals stay clear.
