"""Configuration management for Quote Vault."""

import os
from pathlib import Path


def get_database_path() -> Path:
    """
    Get the database file path from environment or use default.

    Returns:
        Path: Absolute path to the database file
    """
    env_path = os.getenv("QUOTE_VAULT_DB_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    # Default location: ~/.quote-vault/quotes.db
    default_dir = Path.home() / ".quote-vault"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir / "quotes.db"


def get_auto_seed() -> bool:
    """
    Check if database should be automatically seeded on first run.

    Returns:
        bool: True if auto-seeding is enabled
    """
    env_value = os.getenv("QUOTE_VAULT_AUTO_SEED", "true").lower()
    return env_value in ("true", "1", "yes")


def get_log_level() -> str:
    """
    Get logging level from environment or use default.

    Returns:
        str: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    return os.getenv("QUOTE_VAULT_LOG_LEVEL", "INFO").upper()
