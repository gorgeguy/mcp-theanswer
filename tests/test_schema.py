"""Tests for database schema."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from mcp_theanswer.database.schema import (
    SCHEMA_VERSION,
    check_if_seeded,
    get_schema_version,
    init_database,
    migrate_database,
)


@pytest.fixture
def temp_db() -> Path:
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_should_initialize_database_and_create_tables(temp_db: Path) -> None:
    """Test that init_database creates all required tables."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "quotes" in tables
    assert "tags" in tables
    assert "quote_tags" in tables
    assert "schema_version" in tables


def test_should_create_quotes_table_with_correct_schema(temp_db: Path) -> None:
    """Test that quotes table has correct columns."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("PRAGMA table_info(quotes)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
    conn.close()

    assert "id" in columns
    assert "text" in columns
    assert "author" in columns
    assert "source" in columns
    assert "year" in columns
    assert "created_at" in columns


def test_should_create_tags_table_with_correct_schema(temp_db: Path) -> None:
    """Test that tags table has correct columns."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("PRAGMA table_info(tags)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    conn.close()

    assert "id" in columns
    assert "name" in columns


def test_should_create_quote_tags_junction_table(temp_db: Path) -> None:
    """Test that quote_tags junction table exists with foreign keys."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("PRAGMA table_info(quote_tags)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    conn.close()

    assert "quote_id" in columns
    assert "tag_id" in columns


def test_should_create_indices(temp_db: Path) -> None:
    """Test that indices are created."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
    indices = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "idx_quotes_author" in indices
    assert "idx_tags_name" in indices


def test_should_record_schema_version(temp_db: Path) -> None:
    """Test that schema version is recorded."""
    init_database(temp_db)

    version = get_schema_version(temp_db)

    assert version == SCHEMA_VERSION


def test_should_not_duplicate_schema_version_on_reinit(temp_db: Path) -> None:
    """Test that reinitializing doesn't duplicate schema version."""
    init_database(temp_db)
    init_database(temp_db)  # Run twice

    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1


def test_should_return_false_when_database_not_seeded(temp_db: Path) -> None:
    """Test check_if_seeded returns False for empty database."""
    init_database(temp_db)

    result = check_if_seeded(temp_db)

    assert result is False


def test_should_return_false_when_database_does_not_exist() -> None:
    """Test check_if_seeded returns False for non-existent database."""
    non_existent_db = Path("/tmp/does_not_exist_12345.db")

    result = check_if_seeded(non_existent_db)

    assert result is False


def test_should_return_true_when_database_has_quotes(temp_db: Path) -> None:
    """Test check_if_seeded returns True when quotes exist."""
    init_database(temp_db)

    # Add a quote
    conn = sqlite3.connect(temp_db)
    conn.execute(
        "INSERT INTO quotes (text, author) VALUES (?, ?)",
        ("Test quote", "Test Author"),
    )
    conn.commit()
    conn.close()

    result = check_if_seeded(temp_db)

    assert result is True


def test_should_return_none_for_nonexistent_database_version() -> None:
    """Test get_schema_version returns None for non-existent database."""
    non_existent_db = Path("/tmp/does_not_exist_12345.db")

    version = get_schema_version(non_existent_db)

    assert version is None


def test_should_enforce_foreign_key_constraints(temp_db: Path) -> None:
    """Test that foreign key constraints are enforced."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    conn.execute("PRAGMA foreign_keys = ON")

    # Try to insert into quote_tags with non-existent quote_id
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO quote_tags (quote_id, tag_id) VALUES (?, ?)", (999, 999))

    conn.close()


def test_should_cascade_delete_quote_tags_when_quote_deleted(temp_db: Path) -> None:
    """Test that deleting a quote cascades to quote_tags."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    conn.execute("PRAGMA foreign_keys = ON")

    # Insert quote and tag
    cursor = conn.execute("INSERT INTO quotes (text, author) VALUES (?, ?)", ("Test", "Author"))
    quote_id = cursor.lastrowid

    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", ("test",))
    tag_id = cursor.lastrowid

    conn.execute("INSERT INTO quote_tags (quote_id, tag_id) VALUES (?, ?)", (quote_id, tag_id))
    conn.commit()

    # Delete the quote
    conn.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()

    # Check that quote_tags entry was also deleted
    cursor = conn.execute("SELECT COUNT(*) FROM quote_tags WHERE quote_id = ?", (quote_id,))
    count = cursor.fetchone()[0]

    conn.close()

    assert count == 0


def test_should_raise_not_implemented_for_migration() -> None:
    """Test that migrate_database raises NotImplementedError."""
    temp_path = Path("/tmp/test.db")

    with pytest.raises(NotImplementedError):
        migrate_database(temp_path, 1, 2)


def test_should_enforce_unique_tag_names(temp_db: Path) -> None:
    """Test that tag names must be unique."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    conn.execute("INSERT INTO tags (name) VALUES (?)", ("philosophy",))
    conn.commit()

    # Try to insert duplicate
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tags (name) VALUES (?)", ("philosophy",))
        conn.commit()

    conn.close()
