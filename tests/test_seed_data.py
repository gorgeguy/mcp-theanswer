"""Tests for seed data functionality."""

import tempfile
from pathlib import Path

import pytest

from mcp_theanswer.database.operations import (
    get_all_quotes,
    get_quotes_by_author,
    get_quotes_by_tag,
)
from mcp_theanswer.database.schema import init_database
from mcp_theanswer.seed_data import SEED_QUOTES, seed_database


@pytest.fixture
def temp_db() -> Path:
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    init_database(db_path)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_should_have_at_least_15_seed_quotes() -> None:
    """Test that SEED_QUOTES contains at least 15 quotes."""
    assert len(SEED_QUOTES) >= 15


def test_should_have_famous_42_quote() -> None:
    """Test that the famous '42' quote is included."""
    texts = [q["text"] for q in SEED_QUOTES]
    assert any("forty-two" in text.lower() for text in texts)


def test_should_have_dont_panic_quote() -> None:
    """Test that the famous 'Don't Panic' quote is included."""
    texts = [q["text"] for q in SEED_QUOTES]
    assert any("don't panic" in text.lower() for text in texts)


def test_should_have_all_required_fields() -> None:
    """Test that all seed quotes have required fields."""
    for quote in SEED_QUOTES:
        assert "text" in quote
        assert "author" in quote
        assert quote["text"]  # not empty
        assert quote["author"]  # not empty


def test_should_have_metadata_fields() -> None:
    """Test that seed quotes have source, year, and tags."""
    for quote in SEED_QUOTES:
        assert "source" in quote
        assert "year" in quote
        assert "tags" in quote


def test_should_have_variety_of_tags() -> None:
    """Test that seed quotes have a variety of tags."""
    all_tags = set()
    for quote in SEED_QUOTES:
        if quote.get("tags"):
            all_tags.update(quote["tags"])

    # Should have at least several different tag types
    assert len(all_tags) >= 10
    # Should include key themes
    assert "philosophy" in all_tags
    assert "humor" in all_tags


def test_should_all_be_by_douglas_adams() -> None:
    """Test that all quotes are attributed to Douglas Adams."""
    for quote in SEED_QUOTES:
        assert quote["author"] == "Douglas Adams"


def test_should_have_variety_of_sources() -> None:
    """Test that quotes come from various Douglas Adams works."""
    sources = {q["source"] for q in SEED_QUOTES if q.get("source")}
    # Should have quotes from multiple books
    assert len(sources) >= 5


def test_should_seed_empty_database(temp_db: Path) -> None:
    """Test seeding an empty database."""
    added, total = seed_database(temp_db)

    assert added == len(SEED_QUOTES)
    assert total == len(SEED_QUOTES)


def test_should_not_duplicate_on_second_seed(temp_db: Path) -> None:
    """Test that seeding twice doesn't create duplicates."""
    # First seed
    added1, total1 = seed_database(temp_db)
    assert added1 == len(SEED_QUOTES)

    # Second seed (should skip)
    added2, total2 = seed_database(temp_db)
    assert added2 == 0
    assert total2 == total1


def test_should_force_seed_when_requested(temp_db: Path) -> None:
    """Test that force=True allows re-seeding."""
    # First seed
    seed_database(temp_db)

    # Force second seed
    added, total = seed_database(temp_db, force=True)

    assert added == len(SEED_QUOTES)
    assert total == len(SEED_QUOTES) * 2  # Now has duplicates


def test_should_create_quotes_with_all_fields(temp_db: Path) -> None:
    """Test that seeded quotes have all expected fields."""
    seed_database(temp_db)

    quotes = get_all_quotes(temp_db)
    assert len(quotes) == len(SEED_QUOTES)

    # Check first quote has all fields
    quote = quotes[0]
    assert quote.id > 0
    assert quote.text
    assert quote.author == "Douglas Adams"
    assert quote.source
    assert quote.year
    assert quote.created_at
    assert quote.tags


def test_should_create_quotes_searchable_by_author(temp_db: Path) -> None:
    """Test that seeded quotes can be searched by author."""
    seed_database(temp_db)

    quotes = get_quotes_by_author(temp_db, "Douglas Adams")
    assert len(quotes) == len(SEED_QUOTES)


def test_should_create_quotes_searchable_by_tag(temp_db: Path) -> None:
    """Test that seeded quotes can be searched by tag."""
    seed_database(temp_db)

    # Search for philosophy quotes
    philosophy_quotes = get_quotes_by_tag(temp_db, "philosophy")
    assert len(philosophy_quotes) > 0

    # Search for humor quotes
    humor_quotes = get_quotes_by_tag(temp_db, "humor")
    assert len(humor_quotes) > 0


def test_should_preserve_quote_text_exactly(temp_db: Path) -> None:
    """Test that quote text is preserved exactly as in seed data."""
    seed_database(temp_db)

    quotes = get_all_quotes(temp_db)
    seeded_texts = {q["text"] for q in SEED_QUOTES}
    db_texts = {q.text for q in quotes}

    assert db_texts == seeded_texts


def test_should_preserve_all_tags(temp_db: Path) -> None:
    """Test that all tags from seed data are created."""
    seed_database(temp_db)

    quotes = get_all_quotes(temp_db)

    # Collect all tags from seed data
    seed_tags = set()
    for sq in SEED_QUOTES:
        if sq.get("tags"):
            seed_tags.update(sq["tags"])

    # Collect all tags from database
    db_tags = set()
    for quote in quotes:
        if quote.tags:
            db_tags.update(quote.tags)

    assert db_tags == seed_tags


def test_should_return_zero_added_when_already_seeded(temp_db: Path) -> None:
    """Test that return values are correct when database already seeded."""
    # First seed
    seed_database(temp_db)

    # Try to seed again
    added, total = seed_database(temp_db)

    assert added == 0
    assert total == len(SEED_QUOTES)


def test_should_handle_fresh_database_without_init(temp_db: Path) -> None:
    """Test that seeding works even with just initialized database."""
    # temp_db fixture already initializes, so this just confirms it works
    added, total = seed_database(temp_db)

    assert added == len(SEED_QUOTES)
    assert total == len(SEED_QUOTES)
