"""Tests for MCP tools."""

import tempfile
from pathlib import Path

import pytest

from mcp_theanswer.database.operations import add_quote, get_all_quotes
from mcp_theanswer.database.schema import init_database
from mcp_theanswer.mcp.tools import (
    handle_add_quote,
    handle_add_tag_to_quote,
    handle_delete_quote,
    handle_list_tags,
    handle_random_quote,
    handle_search_quotes,
    handle_update_quote,
)


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


@pytest.fixture
def seeded_db(temp_db: Path) -> Path:
    """Create a database with some test quotes."""
    add_quote(
        temp_db,
        text="The answer is 42",
        author="Douglas Adams",
        source="Hitchhiker's Guide",
        year=1979,
        tags=["philosophy", "humor"],
    )
    add_quote(
        temp_db,
        text="Don't Panic",
        author="Douglas Adams",
        source="Hitchhiker's Guide",
        year=1979,
        tags=["humor", "wisdom"],
    )
    add_quote(
        temp_db,
        text="To be or not to be",
        author="William Shakespeare",
        source="Hamlet",
        year=1603,
        tags=["philosophy", "classic"],
    )
    return temp_db


# Tests for add_quote tool


@pytest.mark.asyncio
async def test_should_add_quote_with_all_fields(temp_db: Path) -> None:
    """Test adding a quote with all fields."""
    result = await handle_add_quote(
        temp_db,
        {
            "text": "Test quote",
            "author": "Test Author",
            "source": "Test Source",
            "year": 2024,
            "tags": ["test", "example"],
        },
    )

    assert len(result) == 1
    assert result[0]["type"] == "text"
    assert "Quote added successfully" in result[0]["text"]
    assert "Test quote" in result[0]["text"]
    assert "Test Author" in result[0]["text"]

    # Verify it was actually added
    quotes = get_all_quotes(temp_db)
    assert len(quotes) == 1
    assert quotes[0].text == "Test quote"
    assert quotes[0].author == "Test Author"
    assert quotes[0].source == "Test Source"
    assert quotes[0].year == 2024
    assert set(quotes[0].tags) == {"test", "example"}


@pytest.mark.asyncio
async def test_should_add_quote_with_only_required_fields(temp_db: Path) -> None:
    """Test adding a quote with only text and author."""
    result = await handle_add_quote(temp_db, {"text": "Minimal quote", "author": "Author"})

    assert len(result) == 1
    assert "Quote added successfully" in result[0]["text"]

    quotes = get_all_quotes(temp_db)
    assert len(quotes) == 1
    assert quotes[0].text == "Minimal quote"
    assert quotes[0].author == "Author"
    assert quotes[0].source is None
    assert quotes[0].year is None
    assert quotes[0].tags == []


@pytest.mark.asyncio
async def test_should_reject_empty_text(temp_db: Path) -> None:
    """Test that empty text is rejected."""
    result = await handle_add_quote(temp_db, {"text": "", "author": "Author"})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "text cannot be empty" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_reject_empty_author(temp_db: Path) -> None:
    """Test that empty author is rejected."""
    result = await handle_add_quote(temp_db, {"text": "Test", "author": ""})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "Author name cannot be empty" in result[0]["text"]


# Tests for search_quotes tool


@pytest.mark.asyncio
async def test_should_search_by_query(seeded_db: Path) -> None:
    """Test searching quotes by query text."""
    result = await handle_search_quotes(seeded_db, {"query": "42"})

    assert len(result) == 1
    assert "Found 1 quote" in result[0]["text"]
    assert "The answer is 42" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_search_by_author(seeded_db: Path) -> None:
    """Test searching quotes by author."""
    result = await handle_search_quotes(seeded_db, {"author": "Douglas Adams"})

    assert len(result) == 1
    assert "Found 2 quote" in result[0]["text"]
    assert "The answer is 42" in result[0]["text"]
    assert "Don't Panic" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_search_by_tag(seeded_db: Path) -> None:
    """Test searching quotes by tag."""
    result = await handle_search_quotes(seeded_db, {"tags": ["philosophy"]})

    assert len(result) == 1
    assert "Found 2 quote" in result[0]["text"]
    assert "The answer is 42" in result[0]["text"]
    assert "To be or not to be" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_search_by_multiple_tags_with_and_logic(seeded_db: Path) -> None:
    """Test searching with multiple tags (quote must have ALL tags)."""
    result = await handle_search_quotes(seeded_db, {"tags": ["philosophy", "humor"]})

    assert len(result) == 1
    assert "Found 1 quote" in result[0]["text"]
    assert "The answer is 42" in result[0]["text"]
    assert "To be or not to be" not in result[0]["text"]


@pytest.mark.asyncio
async def test_should_return_message_when_no_results(temp_db: Path) -> None:
    """Test search with no matching results."""
    result = await handle_search_quotes(temp_db, {"query": "nonexistent"})

    assert len(result) == 1
    assert "No quotes found" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_search_with_combined_filters(seeded_db: Path) -> None:
    """Test searching with multiple filters combined."""
    result = await handle_search_quotes(seeded_db, {"author": "Douglas Adams", "tags": ["humor"]})

    assert len(result) == 1
    assert "Found 2 quote" in result[0]["text"]


# Tests for random_quote tool


@pytest.mark.asyncio
async def test_should_return_random_quote(seeded_db: Path) -> None:
    """Test getting a random quote."""
    result = await handle_random_quote(seeded_db, {})

    assert len(result) == 1
    assert result[0]["type"] == "text"
    # Should contain quote marks and attribution
    assert '"' in result[0]["text"]
    assert "—" in result[0]["text"]
    assert "[Quote ID:" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_return_random_quote_with_tag_filter(seeded_db: Path) -> None:
    """Test getting a random quote filtered by tag."""
    result = await handle_random_quote(seeded_db, {"tag": "classic"})

    assert len(result) == 1
    assert "To be or not to be" in result[0]["text"]
    assert "Shakespeare" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_handle_no_quotes_for_tag(seeded_db: Path) -> None:
    """Test random quote when no quotes match the tag."""
    result = await handle_random_quote(seeded_db, {"tag": "nonexistent"})

    assert len(result) == 1
    assert "No quotes found" in result[0]["text"]
    assert "nonexistent" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_handle_empty_database(temp_db: Path) -> None:
    """Test random quote on empty database."""
    result = await handle_random_quote(temp_db, {})

    assert len(result) == 1
    assert "No quotes found" in result[0]["text"]


# Tests for update_quote tool


@pytest.mark.asyncio
async def test_should_update_quote_text(seeded_db: Path) -> None:
    """Test updating quote text."""
    result = await handle_update_quote(seeded_db, {"id": 1, "text": "Updated text"})

    assert len(result) == 1
    assert "Quote 1 updated successfully" in result[0]["text"]

    quotes = get_all_quotes(seeded_db)
    updated = next(q for q in quotes if q.id == 1)
    assert updated.text == "Updated text"


@pytest.mark.asyncio
async def test_should_update_multiple_fields(seeded_db: Path) -> None:
    """Test updating multiple fields at once."""
    result = await handle_update_quote(
        seeded_db, {"id": 1, "author": "New Author", "year": 2024, "source": "New Source"}
    )

    assert "updated successfully" in result[0]["text"]

    quotes = get_all_quotes(seeded_db)
    updated = next(q for q in quotes if q.id == 1)
    assert updated.author == "New Author"
    assert updated.year == 2024
    assert updated.source == "New Source"


@pytest.mark.asyncio
async def test_should_update_tags(seeded_db: Path) -> None:
    """Test updating tags (replaces all existing)."""
    result = await handle_update_quote(seeded_db, {"id": 1, "tags": ["new1", "new2"]})

    assert "updated successfully" in result[0]["text"]

    quotes = get_all_quotes(seeded_db)
    updated = next(q for q in quotes if q.id == 1)
    assert set(updated.tags) == {"new1", "new2"}


@pytest.mark.asyncio
async def test_should_handle_nonexistent_quote_update(seeded_db: Path) -> None:
    """Test updating a quote that doesn't exist."""
    result = await handle_update_quote(seeded_db, {"id": 999, "text": "New text"})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "not found" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_reject_update_with_no_fields(seeded_db: Path) -> None:
    """Test update with only ID (no fields to update)."""
    result = await handle_update_quote(seeded_db, {"id": 1})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "No fields specified" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_reject_update_with_empty_text(seeded_db: Path) -> None:
    """Test that empty text is rejected in update."""
    result = await handle_update_quote(seeded_db, {"id": 1, "text": ""})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "text cannot be empty" in result[0]["text"]


# Tests for delete_quote tool


@pytest.mark.asyncio
async def test_should_delete_quote(seeded_db: Path) -> None:
    """Test deleting a quote."""
    result = await handle_delete_quote(seeded_db, {"id": 1})

    assert len(result) == 1
    assert "Quote 1 deleted successfully" in result[0]["text"]

    quotes = get_all_quotes(seeded_db)
    assert len(quotes) == 2
    assert not any(q.id == 1 for q in quotes)


@pytest.mark.asyncio
async def test_should_handle_nonexistent_quote_delete(seeded_db: Path) -> None:
    """Test deleting a quote that doesn't exist."""
    result = await handle_delete_quote(seeded_db, {"id": 999})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "not found" in result[0]["text"]


# Tests for add_tag_to_quote tool


@pytest.mark.asyncio
async def test_should_add_tag_to_quote(seeded_db: Path) -> None:
    """Test adding a tag to an existing quote."""
    result = await handle_add_tag_to_quote(seeded_db, {"quote_id": 1, "tag": "newtag"})

    assert len(result) == 1
    assert "Tag 'newtag' added to quote 1 successfully" in result[0]["text"]

    quotes = get_all_quotes(seeded_db)
    quote = next(q for q in quotes if q.id == 1)
    assert "newtag" in quote.tags


@pytest.mark.asyncio
async def test_should_handle_duplicate_tag_gracefully(seeded_db: Path) -> None:
    """Test adding a tag that already exists on the quote."""
    result = await handle_add_tag_to_quote(seeded_db, {"quote_id": 1, "tag": "humor"})

    # Should succeed (idempotent)
    assert len(result) == 1
    assert "added" in result[0]["text"] or "successfully" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_handle_nonexistent_quote_add_tag(seeded_db: Path) -> None:
    """Test adding a tag to a quote that doesn't exist."""
    result = await handle_add_tag_to_quote(seeded_db, {"quote_id": 999, "tag": "newtag"})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "not found" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_reject_empty_tag(seeded_db: Path) -> None:
    """Test that empty tag name is rejected."""
    result = await handle_add_tag_to_quote(seeded_db, {"quote_id": 1, "tag": ""})

    assert len(result) == 1
    assert "Error" in result[0]["text"]
    assert "tag name cannot be empty" in result[0]["text"].lower()


# Tests for list_tags tool


@pytest.mark.asyncio
async def test_should_list_all_tags(seeded_db: Path) -> None:
    """Test listing all tags with counts."""
    result = await handle_list_tags(seeded_db, {})

    assert len(result) == 1
    assert "Found" in result[0]["text"]
    assert "tag(s)" in result[0]["text"]
    # Should include all tags from seeded data
    assert "philosophy" in result[0]["text"]
    assert "humor" in result[0]["text"]
    assert "wisdom" in result[0]["text"]
    assert "classic" in result[0]["text"]


@pytest.mark.asyncio
async def test_should_show_tag_counts(seeded_db: Path) -> None:
    """Test that tag counts are displayed."""
    result = await handle_list_tags(seeded_db, {})

    text = result[0]["text"]
    # Philosophy appears in 2 quotes
    assert "philosophy" in text
    # Humor appears in 2 quotes
    assert "humor" in text
    # Each tag should show its count
    assert "quote(s)" in text


@pytest.mark.asyncio
async def test_should_handle_no_tags(temp_db: Path) -> None:
    """Test listing tags when none exist."""
    result = await handle_list_tags(temp_db, {})

    assert len(result) == 1
    assert "No tags found" in result[0]["text"]
