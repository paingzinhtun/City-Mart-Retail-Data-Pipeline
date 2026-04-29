"""Database configuration for the City Mart retail pipeline.

Values are read from environment variables first so the project can be reused
across local machines, CI jobs, and production-like deployments without code
changes.
"""

import os


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "city_mart"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}
