"""Build warehouse star-schema CSV tables from staging data."""

from __future__ import annotations

import pandas as pd


def build_dim_products(staging_products: pd.DataFrame) -> pd.DataFrame:
    """Build the product dimension with a simple surrogate key."""
    dim = staging_products[["product_id", "product_name", "category"]].copy()
    dim = dim.sort_values("product_id").drop_duplicates("product_id").reset_index(drop=True)
    dim.insert(0, "product_key", range(1, len(dim) + 1))
    return dim


def build_dim_stores(staging_stores: pd.DataFrame) -> pd.DataFrame:
    """Build the store dimension with a simple surrogate key."""
    dim = staging_stores[["store_id", "store_name", "store_city"]].copy()
    dim = dim.sort_values("store_id").drop_duplicates("store_id").reset_index(drop=True)
    dim.insert(0, "store_key", range(1, len(dim) + 1))
    return dim


def build_dim_dates(staging_sales: pd.DataFrame) -> pd.DataFrame:
    """Build a date dimension from distinct sale dates."""
    dates = pd.to_datetime(staging_sales["sale_date"]).drop_duplicates().sort_values()
    dim = pd.DataFrame({"full_date": dates})
    dim["date_key"] = dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim["day"] = dim["full_date"].dt.day
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.month_name()
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["year"] = dim["full_date"].dt.year
    dim["day_of_week"] = dim["full_date"].dt.day_name()
    return dim[
        ["date_key", "full_date", "day", "month", "month_name", "quarter", "year", "day_of_week"]
    ].reset_index(drop=True)


def build_fact_sales(
    staging_sales: pd.DataFrame,
    dim_products: pd.DataFrame,
    dim_stores: pd.DataFrame,
    dim_dates: pd.DataFrame,
) -> pd.DataFrame:
    """Build fact sales by joining staging sales to dimensions."""
    fact = staging_sales.copy()
    fact["sale_date_key"] = pd.to_datetime(fact["sale_date"]).dt.strftime("%Y%m%d").astype(int)

    fact = fact.merge(dim_products[["product_key", "product_id"]], on="product_id", how="left")
    fact = fact.merge(dim_stores[["store_key", "store_id"]], on="store_id", how="left")
    fact = fact.merge(dim_dates[["date_key"]], left_on="sale_date_key", right_on="date_key", how="left")

    return fact[
        [
            "sale_id",
            "date_key",
            "product_key",
            "store_key",
            "units_sold",
            "unit_sale_price_ks",
            "unit_cost_ks",
            "revenue_ks",
            "profit_ks",
            "payment_method",
        ]
    ].sort_values(["date_key", "sale_id"]).reset_index(drop=True)


def build_warehouse_tables(
    staging_products: pd.DataFrame,
    staging_stores: pd.DataFrame,
    staging_sales: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build all warehouse tables used by the project."""
    dim_products = build_dim_products(staging_products)
    dim_stores = build_dim_stores(staging_stores)
    dim_dates = build_dim_dates(staging_sales)
    fact_sales = build_fact_sales(staging_sales, dim_products, dim_stores, dim_dates)

    return {
        "dim_products": dim_products,
        "dim_stores": dim_stores,
        "dim_dates": dim_dates,
        "fact_sales": fact_sales,
    }
