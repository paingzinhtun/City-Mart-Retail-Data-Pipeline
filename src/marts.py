"""Build business-friendly mart CSV tables from warehouse data."""

from __future__ import annotations

import pandas as pd


def build_mart_daily_revenue(fact_sales: pd.DataFrame, dim_dates: pd.DataFrame) -> pd.DataFrame:
    """Summarize revenue and profit by day."""
    sales = fact_sales.merge(dim_dates[["date_key", "full_date"]], on="date_key", how="left")
    mart = (
        sales.groupby(["full_date"], as_index=False)
        .agg(
            total_units_sold=("units_sold", "sum"),
            total_revenue_ks=("revenue_ks", "sum"),
            total_profit_ks=("profit_ks", "sum"),
            transaction_count=("sale_id", "nunique"),
        )
        .sort_values("full_date")
    )
    return mart


def build_mart_top_products(fact_sales: pd.DataFrame, dim_products: pd.DataFrame) -> pd.DataFrame:
    """Rank products by total revenue."""
    sales = fact_sales.merge(dim_products, on="product_key", how="left")
    mart = (
        sales.groupby(["product_id", "product_name", "category"], as_index=False)
        .agg(
            total_units_sold=("units_sold", "sum"),
            total_revenue_ks=("revenue_ks", "sum"),
            total_profit_ks=("profit_ks", "sum"),
            transaction_count=("sale_id", "nunique"),
        )
        .sort_values(["total_revenue_ks", "total_units_sold"], ascending=[False, False])
        .reset_index(drop=True)
    )
    mart.insert(0, "product_rank", range(1, len(mart) + 1))
    return mart


def build_mart_category_profit(fact_sales: pd.DataFrame, dim_products: pd.DataFrame) -> pd.DataFrame:
    """Summarize revenue and profit by product category."""
    sales = fact_sales.merge(dim_products[["product_key", "category"]], on="product_key", how="left")
    mart = (
        sales.groupby(["category"], as_index=False)
        .agg(
            total_units_sold=("units_sold", "sum"),
            total_revenue_ks=("revenue_ks", "sum"),
            total_profit_ks=("profit_ks", "sum"),
        )
        .sort_values("total_profit_ks", ascending=False)
        .reset_index(drop=True)
    )
    return mart


def build_mart_tables(warehouse_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Build all mart tables from warehouse tables."""
    fact_sales = warehouse_tables["fact_sales"]
    dim_products = warehouse_tables["dim_products"]
    dim_dates = warehouse_tables["dim_dates"]

    return {
        "mart_daily_revenue": build_mart_daily_revenue(fact_sales, dim_dates),
        "mart_top_products": build_mart_top_products(fact_sales, dim_products),
        "mart_category_profit": build_mart_category_profit(fact_sales, dim_products),
    }
