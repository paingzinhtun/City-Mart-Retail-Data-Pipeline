"""Generate a small simulated daily sales CSV for practice runs."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date
from pathlib import Path


PRODUCTS = [
    ("P001", "Jasmine Rice 5kg", "Rice & Grains", 14500, 10150),
    ("P002", "Sunflower Oil 1L", "Cooking Oil", 7800, 5460),
    ("P003", "Instant Coffee 20 Sachets", "Beverages", 6500, 4550),
    ("P004", "Shampoo 650ml", "Personal Care", 11900, 8330),
    ("P005", "Fresh Milk 1L", "Dairy", 3900, 2730),
]

STORES = [
    ("S001", "City Mart Junction City", "Yangon"),
    ("S002", "City Mart Myanmar Plaza", "Yangon"),
    ("S003", "City Mart Mandalay Central", "Mandalay"),
]

PAYMENT_METHODS = ["Cash", "Card", "Mobile Wallet"]


def generate_sales(sale_date: date, row_count: int) -> list[dict[str, object]]:
    """Create simulated retail sales rows."""
    rows: list[dict[str, object]] = []
    for index in range(1, row_count + 1):
        product_id, product_name, category, sale_price, unit_cost = random.choice(PRODUCTS)
        store_id, store_name, store_city = random.choice(STORES)
        rows.append(
            {
                "sale_id": f"{sale_date:%Y%m%d}-{index:04d}",
                "sale_date": sale_date.isoformat(),
                "store_id": store_id,
                "store_name": store_name,
                "store_city": store_city,
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "units_sold": random.randint(1, 5),
                "unit_sale_price_ks": sale_price,
                "unit_cost_ks": unit_cost,
                "payment_method": random.choice(PAYMENT_METHODS),
            }
        )
    return rows


def write_sales(rows: list[dict[str, object]], output_path: Path) -> None:
    """Write generated sales rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    """Parse generator command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate simulated City Mart-style raw sales data.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Sale date in YYYY-MM-DD format.")
    parser.add_argument("--rows", type=int, default=25, help="Number of rows to generate.")
    parser.add_argument("--output-dir", default="data/raw", help="Directory for generated raw CSV.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sale_date = date.fromisoformat(args.date)
    output = Path(args.output_dir) / f"daily_sales_{sale_date:%Y_%m_%d}.csv"
    write_sales(generate_sales(sale_date, args.rows), output)
    print(f"Wrote {args.rows} rows to {output}")
