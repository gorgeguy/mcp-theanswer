"""Database schema and initialization."""

import sqlite3
from pathlib import Path

# Schema version for future migrations
SCHEMA_VERSION = 1

# SQL statements for creating tables
CREATE_QUOTES_TABLE = """
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    author TEXT NOT NULL,
    source TEXT,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
"""

CREATE_QUOTE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS quote_tags (
    quote_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (quote_id, tag_id),
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
"""

CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL statements for creating indices
CREATE_QUOTES_AUTHOR_INDEX = """
CREATE INDEX IF NOT EXISTS idx_quotes_author ON quotes(author);
"""

CREATE_TAGS_NAME_INDEX = """
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
"""


def init_database(db_path: Path) -> None:
    """
    Initialize the database with schema and indices.

    Creates all tables and indices if they don't exist.
    Records the schema version for future migrations.

    Args:
        db_path: Path to the database file
    """
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")

        # Create tables
        conn.execute(CREATE_QUOTES_TABLE)
        conn.execute(CREATE_TAGS_TABLE)
        conn.execute(CREATE_QUOTE_TAGS_TABLE)
        conn.execute(CREATE_SCHEMA_VERSION_TABLE)

        # Create indices
        conn.execute(CREATE_QUOTES_AUTHOR_INDEX)
        conn.execute(CREATE_TAGS_NAME_INDEX)

        # Record schema version if not already recorded
        cursor = conn.execute(
            "SELECT version FROM schema_version WHERE version = ?", (SCHEMA_VERSION,)
        )
        if not cursor.fetchone():
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

        conn.commit()
    finally:
        conn.close()


def check_if_seeded(db_path: Path) -> bool:
    """
    Check if the database has been seeded with initial data.

    Args:
        db_path: Path to the database file

    Returns:
        bool: True if database contains quotes, False otherwise
    """
    if not db_path.exists():
        return False

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM quotes")
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return False
    finally:
        conn.close()


def get_schema_version(db_path: Path) -> int | None:
    """
    Get the current schema version of the database.

    Args:
        db_path: Path to the database file

    Returns:
        int | None: Current schema version, or None if not initialized
    """
    if not db_path.exists():
        return None

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        result = cursor.fetchone()
        return result[0] if result and result[0] else None
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return None
    finally:
        conn.close()


def migrate_database(db_path: Path, from_version: int, to_version: int) -> None:
    """
    Migrate database schema from one version to another.

    This is a placeholder for future schema migrations.

    Args:
        db_path: Path to the database file
        from_version: Current schema version
        to_version: Target schema version

    Raises:
        NotImplementedError: Migration not yet implemented
    """
    raise NotImplementedError(f"Migration from v{from_version} to v{to_version} not implemented")
