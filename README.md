# City Mart Retail Data Pipeline

## Overview

City Mart Retail Data Pipeline is a batch data engineering project built with Python, pandas, PostgreSQL, and SQL. It simulates how a retail company processes daily sales files from stores, cleans and validates the data, loads it into normalized operational tables, and then builds a star schema warehouse for analytics.

The project is designed to be beginner-friendly, but it follows practical data engineering patterns: modular ETL code, database constraints, UPSERT loading, foreign keys, reusable pipeline execution, and separate OLTP and OLAP models.

## What This Project Does

This pipeline takes raw daily sales CSV files and turns them into analytics-ready database tables.

```text
Raw CSV -> Extract -> Transform -> Load OLTP -> Build OLAP Warehouse -> Analytics Queries
```

Each CSV row represents one product sold in one customer order. The pipeline uses that data to create:

- Clean processed CSV files
- Normalized OLTP tables for transactional data
- Dimensional OLAP tables for reporting
- A sales fact table for revenue analysis
- Example SQL queries for business insights

## Why This Project Is Useful

Retail businesses collect sales data every day, but raw CSV files are not enough for analytics. Data must be cleaned, validated, structured, and loaded into a database before analysts can answer business questions.

This project helps demonstrate how data engineers support business reporting by answering questions like:

- How much revenue did the business make each day?
- Which stores generated the most sales?
- Which products and categories sold best?
- Which customers spent the most?
- Which payment methods are most used?

It is also a strong portfolio project because it shows both Python ETL skills and SQL data modeling skills.

## Tech Stack

- Python 3.10+
- pandas
- psycopg2
- PostgreSQL
- SQL
- PowerShell or terminal

## Project Structure

```text
city_mart_retail_pipeline/
|
|-- config/
|   |-- __init__.py
|   |-- db_config.py
|
|-- data/
|   |-- raw/
|   |   |-- daily_sales_2026_04_28.csv
|   |   |-- daily_sales_2026_04_29.csv
|   |   |-- daily_sales_2026_04_30.csv
|   |   |-- daily_sales_2026_05_01.csv
|   |
|   |-- processed/
|
|-- sql/
|   |-- oltp_schema.sql
|   |-- olap_schema.sql
|   |-- analytics.sql
|
|-- src/
|   |-- __init__.py
|   |-- extract.py
|   |-- transform.py
|   |-- load.py
|   |-- warehouse.py
|   |-- pipeline.py
|
|-- README.md
|-- requirements.txt
```

## Pipeline Architecture

### 1. Extract

File: `src/extract.py`

The extract step:

- Reads a CSV file with pandas
- Checks that the file exists
- Returns a DataFrame for transformation

### 2. Transform

File: `src/transform.py`

The transform step:

- Removes missing required values
- Converts dates, quantities, and prices to correct data types
- Validates `quantity > 0`
- Validates `unit_price >= 0`
- Removes duplicate order-product rows
- Creates the derived column `line_total`

Formula:

```text
line_total = quantity * unit_price
```

### 3. Load OLTP

File: `src/load.py`

The OLTP load step inserts data into normalized PostgreSQL tables:

- `customers`
- `stores`
- `suppliers`
- `categories`
- `products`
- `orders`
- `order_items`

The loader uses UPSERT logic so the same file can be loaded again without creating duplicate records.

### 4. Build OLAP Warehouse

File: `src/warehouse.py`

The warehouse step creates a star schema for analytics:

- `dim_customer`
- `dim_product`
- `dim_store`
- `dim_date`
- `fact_sales`

The `dim_product` table is denormalized and includes:

- Product name
- Category name
- Supplier name

This makes analytics queries easier and faster.

### 5. Run Pipeline

File: `src/pipeline.py`

The runner executes all steps in order:

```text
extract -> transform -> load OLTP -> create OLAP schema -> populate warehouse
```

## Database Design

### OLTP Model

The OLTP model stores transactional business data in normalized tables. It is designed for data integrity and clean relationships.

Important relationships:

- One customer can have many orders
- One store can have many orders
- One order can have many order items
- One product belongs to one category
- One product has one supplier

### OLAP Star Schema

The OLAP model is designed for analytics.

Fact table:

- `fact_sales`

Dimension tables:

- `dim_customer`
- `dim_product`
- `dim_store`
- `dim_date`

This structure makes it easy to calculate sales by date, product, customer, and store.

## Sample Data

The project includes four sample daily sales files:

```text
data/raw/daily_sales_2026_04_28.csv
data/raw/daily_sales_2026_04_29.csv
data/raw/daily_sales_2026_04_30.csv
data/raw/daily_sales_2026_05_01.csv
```

Required CSV columns:

```text
order_id, order_date, customer_id, customer_name, customer_email,
customer_phone, store_id, store_name, store_city, product_id,
product_name, category_id, category_name, supplier_id, supplier_name,
quantity, unit_price, payment_method
```

Example row:

```text
10001,2026-04-28,C001,Aye Aye,aye.aye@example.com,+959400000001,S001,City Mart Junction City,Yangon,P001,Jasmine Rice 5kg,CAT01,Rice & Grains,SUP01,Golden Farm Co.,2,14500.00,Cash
```

## Step-by-Step Setup

### Step 1: Clone or Open the Project

Open PowerShell in the project folder:

```powershell
cd C:\Users\HP\Desktop\city_mart_retail_pipeline
```

### Step 2: Create PostgreSQL Database

Open pgAdmin or `psql`, then run:

```sql
CREATE DATABASE city_mart;
```

### Step 3: Configure Database Credentials

Set the database connection values in PowerShell:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "city_mart"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "your_postgres_password"
```

Replace `your_postgres_password` with your real PostgreSQL password.

Default values are also defined in:

```text
config/db_config.py
```

### Step 4: Create Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 6: Run One Daily File

```powershell
python src/pipeline.py --file data/raw/daily_sales_2026_04_28.csv
```

Expected output:

```text
Starting pipeline for: data\raw\daily_sales_2026_04_28.csv
Step 1/6: Extracting CSV data...
Step 2/6: Transforming and validating data...
Step 3/6: Creating OLTP schema...
Step 4/6: Loading OLTP tables...
Step 5/6: Creating OLAP schema...
Step 6/6: Populating warehouse star schema...
Pipeline completed successfully.
```

### Step 7: Load All Sample Files

Run each file:

```powershell
python src/pipeline.py --file data/raw/daily_sales_2026_04_28.csv
python src/pipeline.py --file data/raw/daily_sales_2026_04_29.csv
python src/pipeline.py --file data/raw/daily_sales_2026_04_30.csv
python src/pipeline.py --file data/raw/daily_sales_2026_05_01.csv
```

Processed versions of the files are saved in:

```text
data/processed/
```

## Verify the Load

After loading all sample files, connect to the `city_mart` database and run:

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM stores;
SELECT COUNT(*) FROM suppliers;
SELECT COUNT(*) FROM categories;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;
SELECT COUNT(*) FROM dim_customer;
SELECT COUNT(*) FROM dim_product;
SELECT COUNT(*) FROM dim_store;
SELECT COUNT(*) FROM dim_date;
SELECT COUNT(*) FROM fact_sales;
```

Expected counts after all four sample files:

```text
customers: 17
stores: 6
suppliers: 13
categories: 12
products: 27
orders: 20
order_items: 33
dim_customer: 17
dim_product: 27
dim_store: 6
dim_date: 4
fact_sales: 33
```

## Example Analytics

All analytics examples are stored in:

```text
sql/analytics.sql
```

### Daily Revenue

```sql
SELECT
    d.full_date,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.line_total) AS revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;
```

### Revenue by Store

```sql
SELECT
    s.store_name,
    s.city,
    SUM(f.line_total) AS revenue
FROM fact_sales f
JOIN dim_store s ON f.store_key = s.store_key
GROUP BY s.store_name, s.city
ORDER BY revenue DESC;
```

### Top Products

```sql
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
```

### Customer Spend

```sql
SELECT
    c.customer_name,
    c.email,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.line_total) AS total_spend
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_name, c.email
ORDER BY total_spend DESC;
```

## Key Data Engineering Concepts Demonstrated

- Batch data ingestion
- CSV extraction with pandas
- Data validation and type conversion
- Derived metric creation
- Duplicate handling
- PostgreSQL table design
- Primary keys and foreign keys
- UPSERT loading
- OLTP normalization
- OLAP star schema modeling
- Fact and dimension tables
- SQL analytics queries
- Reusable pipeline orchestration

## Common Issues

### CSV file not found

Make sure the file path exists:

```powershell
python src/pipeline.py --file data/raw/daily_sales_2026_04_28.csv
```

Do not run placeholder names like:

```powershell
python src/pipeline.py --file data/raw/your_new_file.csv
```

unless you actually created that file.

### Database connection failed

Check that:

- PostgreSQL is running
- The `city_mart` database exists
- Your username and password are correct
- Environment variables are set in the same terminal session

### PowerShell cannot activate virtual environment

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Production Improvement Ideas

This project is intentionally simple enough to learn from, but it can be extended with:

- A `run_all.py` script to load every CSV automatically
- Logging with Python's `logging` module
- Unit tests for transformation rules
- Data quality reports
- Rejected records table
- Staging tables before final OLTP load
- Incremental warehouse loading by date
- Airflow or Prefect orchestration
- Docker Compose for PostgreSQL setup
- Dashboarding with Power BI, Metabase, or Superset

## Repository Description

Suggested GitHub repository description:

```text
A production-minded batch ETL pipeline using Python, pandas, PostgreSQL, and star schema modeling for retail sales analytics.
```

Suggested topics:

```text
python, postgresql, pandas, etl, data-engineering, batch-pipeline, data-pipeline, star-schema, olap, oltp, retail-analytics, sql
```
