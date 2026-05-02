"""PostgreSQL configuration loaded from `.env` and environment variables."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_env_file(env_path: Path = PROJECT_ROOT / ".env") -> None:
    """Load simple KEY=VALUE lines from a local .env file if present."""
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue
        key, value = cleaned.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "city_mart"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def validate_db_config() -> None:
    """Fail early when required PostgreSQL settings are missing."""
    missing = [key for key, value in DB_CONFIG.items() if value in ("", None)]
    if missing:
        missing_names = ", ".join(f"DB_{key.upper()}" if key != "dbname" else "DB_NAME" for key in missing)
        raise ValueError(
            f"Missing PostgreSQL configuration: {missing_names}. "
            "Create a .env file from .env.example and set your local database values."
        )
