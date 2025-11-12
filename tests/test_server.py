"""Tests for server initialization and setup."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_theanswer.database.schema import check_if_seeded, get_schema_version
from mcp_theanswer.server import setup_database


@pytest.fixture
def temp_db_dir(monkeypatch):
    """Create a temporary directory for database testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_quotes.db"
        # Mock environment to use temp database
        monkeypatch.setenv("QUOTE_VAULT_DB_PATH", str(db_path))
        monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "false")
        monkeypatch.setenv("QUOTE_VAULT_LOG_LEVEL", "ERROR")
        yield db_path
        # Cleanup happens automatically with temp directory


def test_should_create_database_directory_if_not_exists(temp_db_dir: Path) -> None:
    """Test that setup_database creates parent directory if it doesn't exist."""
    # Remove the directory to ensure it doesn't exist
    if temp_db_dir.parent.exists():
        import shutil

        shutil.rmtree(temp_db_dir.parent)

    db_path = setup_database()

    assert db_path.parent.exists()
    assert db_path.exists()


def test_should_initialize_database_schema(temp_db_dir: Path) -> None:
    """Test that setup_database initializes the database schema."""
    db_path = setup_database()

    # Check that schema version is set
    version = get_schema_version(db_path)
    assert version == 1


def test_should_not_seed_when_auto_seed_disabled(temp_db_dir: Path, monkeypatch) -> None:
    """Test that database is not seeded when auto_seed is false."""
    monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "false")

    db_path = setup_database()

    # Database should be initialized but not seeded
    assert db_path.exists()
    assert not check_if_seeded(db_path)


def test_should_seed_when_auto_seed_enabled(temp_db_dir: Path, monkeypatch) -> None:
    """Test that database is seeded when auto_seed is true."""
    monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "true")

    db_path = setup_database()

    # Database should be initialized and seeded
    assert db_path.exists()
    assert check_if_seeded(db_path)


def test_should_not_seed_if_already_seeded(temp_db_dir: Path, monkeypatch) -> None:
    """Test that database is not re-seeded if already contains data."""
    monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "true")

    # First setup - should seed
    db_path = setup_database()
    assert check_if_seeded(db_path)

    # Get initial quote count
    from mcp_theanswer.database.operations import get_all_quotes

    initial_quotes = get_all_quotes(db_path)
    initial_count = len(initial_quotes)

    # Second setup - should not seed again
    db_path = setup_database()
    final_quotes = get_all_quotes(db_path)
    final_count = len(final_quotes)

    assert final_count == initial_count


def test_should_use_environment_database_path(monkeypatch) -> None:
    """Test that QUOTE_VAULT_DB_PATH environment variable is respected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_path = Path(tmpdir) / "custom" / "quotes.db"
        monkeypatch.setenv("QUOTE_VAULT_DB_PATH", str(custom_path))
        monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "false")

        db_path = setup_database()

        # Resolve both paths to handle symlinks (e.g., /var vs /private/var on macOS)
        assert db_path.resolve() == custom_path.resolve()
        assert db_path.exists()


def test_should_use_default_path_when_no_env_var(monkeypatch) -> None:
    """Test that default path is used when no environment variable is set."""
    monkeypatch.delenv("QUOTE_VAULT_DB_PATH", raising=False)
    monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "false")

    db_path = setup_database()

    # Should use ~/.quote-vault/quotes.db
    assert ".quote-vault" in str(db_path)
    assert db_path.name == "quotes.db"
    assert db_path.exists()

    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_should_handle_various_auto_seed_values(temp_db_dir: Path, monkeypatch) -> None:
    """Test that auto_seed recognizes various truthy/falsy values."""
    # Test truthy values
    for value in ["true", "True", "TRUE", "1", "yes", "YES"]:
        # Clean database
        if temp_db_dir.exists():
            temp_db_dir.unlink()

        monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", value)
        db_path = setup_database()
        assert check_if_seeded(db_path), f"Failed for value: {value}"

    # Test falsy values
    for value in ["false", "False", "FALSE", "0", "no", "NO"]:
        # Clean database
        if temp_db_dir.exists():
            temp_db_dir.unlink()

        monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", value)
        db_path = setup_database()
        assert not check_if_seeded(db_path), f"Failed for value: {value}"


def test_should_continue_if_seeding_fails(temp_db_dir: Path, monkeypatch) -> None:
    """Test that server continues if seeding fails."""
    monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "true")

    # Mock seed_database to raise an exception
    with patch("mcp_theanswer.server.seed_database") as mock_seed:
        mock_seed.side_effect = Exception("Seeding failed")

        # Should not raise, just continue
        db_path = setup_database()

        # Database should still be initialized
        assert db_path.exists()
        assert get_schema_version(db_path) == 1


def test_should_raise_if_database_init_fails(temp_db_dir: Path, monkeypatch) -> None:
    """Test that setup fails if database initialization fails."""
    monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "false")

    # Mock init_database to raise an exception
    with patch("mcp_theanswer.server.init_database") as mock_init:
        mock_init.side_effect = Exception("Init failed")

        # Should raise the exception
        with pytest.raises(Exception, match="Init failed"):
            setup_database()


def test_should_respect_log_level_from_env(temp_db_dir: Path, monkeypatch) -> None:
    """Test that log level is set from environment variable."""
    import logging

    from mcp_theanswer.server import logger

    # Test different log levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        monkeypatch.setenv("QUOTE_VAULT_LOG_LEVEL", level)
        monkeypatch.setenv("QUOTE_VAULT_AUTO_SEED", "false")

        setup_database()

        assert logger.level == getattr(logging, level)
