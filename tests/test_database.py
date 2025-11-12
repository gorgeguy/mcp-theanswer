"""Tests for database operations."""

import tempfile
from pathlib import Path

import pytest

from mcp_theanswer.database.operations import (
    InvalidInputError,
    add_quote,
    add_tag_to_quote,
    delete_quote,
    get_all_quotes,
    get_quote_by_id,
    get_quotes_by_author,
    get_quotes_by_tag,
    get_random_quote,
    get_statistics,
    list_all_tags,
    search_quotes,
    update_quote,
)
from mcp_theanswer.database.schema import init_database


@pytest.fixture
def test_db() -> Path:
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    init_database(db_path)
    yield db_path
    if db_path.exists():
        db_path.unlink()


# Tests for add_quote


def test_should_add_quote_with_minimal_fields(test_db: Path) -> None:
    """Test adding a quote with only required fields."""
    quote = add_quote(test_db, text="Test quote", author="Test Author")

    assert quote.id > 0
    assert quote.text == "Test quote"
    assert quote.author == "Test Author"
    assert quote.source is None
    assert quote.year is None
    assert quote.tags == []


def test_should_add_quote_with_all_fields(test_db: Path) -> None:
    """Test adding a quote with all fields."""
    quote = add_quote(
        test_db,
        text="The answer is 42",
        author="Douglas Adams",
        source="Hitchhiker's Guide",
        year=1979,
        tags=["philosophy", "humor"],
    )

    assert quote.id > 0
    assert quote.text == "The answer is 42"
    assert quote.author == "Douglas Adams"
    assert quote.source == "Hitchhiker's Guide"
    assert quote.year == 1979
    assert set(quote.tags) == {"philosophy", "humor"}


def test_should_strip_whitespace_from_quote_text_and_author(test_db: Path) -> None:
    """Test that whitespace is stripped from text and author."""
    quote = add_quote(test_db, text="  Test quote  ", author="  Test Author  ")

    assert quote.text == "Test quote"
    assert quote.author == "Test Author"


def test_should_raise_error_when_quote_text_is_empty(test_db: Path) -> None:
    """Test that empty quote text raises error."""
    with pytest.raises(InvalidInputError, match="Quote text cannot be empty"):
        add_quote(test_db, text="", author="Author")


def test_should_raise_error_when_author_is_empty(test_db: Path) -> None:
    """Test that empty author raises error."""
    with pytest.raises(InvalidInputError, match="Author name cannot be empty"):
        add_quote(test_db, text="Quote", author="")


def test_should_raise_error_when_quote_text_is_only_whitespace(test_db: Path) -> None:
    """Test that whitespace-only quote text raises error."""
    with pytest.raises(InvalidInputError):
        add_quote(test_db, text="   ", author="Author")


def test_should_create_tags_automatically_when_adding_quote(test_db: Path) -> None:
    """Test that tags are created if they don't exist."""
    quote1 = add_quote(test_db, text="Quote 1", author="Author", tags=["new_tag"])
    quote2 = add_quote(test_db, text="Quote 2", author="Author", tags=["new_tag"])

    # Both quotes should have the same tag
    assert "new_tag" in quote1.tags
    assert "new_tag" in quote2.tags


def test_should_ignore_empty_tag_names(test_db: Path) -> None:
    """Test that empty or whitespace tag names are ignored."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1", "", "  ", "tag2"])

    assert set(quote.tags) == {"tag1", "tag2"}


# Tests for get_quote_by_id


def test_should_get_quote_by_id(test_db: Path) -> None:
    """Test retrieving a quote by ID."""
    created = add_quote(test_db, text="Test", author="Author", tags=["tag1"])

    retrieved = get_quote_by_id(test_db, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.text == "Test"
    assert retrieved.author == "Author"
    assert retrieved.tags == ["tag1"]


def test_should_return_none_when_quote_id_not_found(test_db: Path) -> None:
    """Test that non-existent ID returns None."""
    result = get_quote_by_id(test_db, 999)

    assert result is None


# Tests for get_all_quotes


def test_should_get_all_quotes(test_db: Path) -> None:
    """Test retrieving all quotes."""
    add_quote(test_db, text="Quote 1", author="Author 1")
    add_quote(test_db, text="Quote 2", author="Author 2")
    add_quote(test_db, text="Quote 3", author="Author 3")

    quotes = get_all_quotes(test_db)

    assert len(quotes) == 3
    # Check all quotes are retrieved
    texts = {q.text for q in quotes}
    assert texts == {"Quote 1", "Quote 2", "Quote 3"}


def test_should_return_empty_list_when_no_quotes(test_db: Path) -> None:
    """Test that empty database returns empty list."""
    quotes = get_all_quotes(test_db)

    assert quotes == []


# Tests for get_quotes_by_author


def test_should_get_quotes_by_author(test_db: Path) -> None:
    """Test retrieving quotes by specific author."""
    add_quote(test_db, text="Quote 1", author="Douglas Adams")
    add_quote(test_db, text="Quote 2", author="Terry Pratchett")
    add_quote(test_db, text="Quote 3", author="Douglas Adams")

    quotes = get_quotes_by_author(test_db, "Douglas Adams")

    assert len(quotes) == 2
    assert all(q.author == "Douglas Adams" for q in quotes)


def test_should_return_empty_list_when_author_not_found(test_db: Path) -> None:
    """Test that non-existent author returns empty list."""
    add_quote(test_db, text="Quote", author="Author")

    quotes = get_quotes_by_author(test_db, "Unknown Author")

    assert quotes == []


# Tests for get_quotes_by_tag


def test_should_get_quotes_by_tag(test_db: Path) -> None:
    """Test retrieving quotes by tag."""
    add_quote(test_db, text="Quote 1", author="Author", tags=["philosophy"])
    add_quote(test_db, text="Quote 2", author="Author", tags=["humor"])
    add_quote(test_db, text="Quote 3", author="Author", tags=["philosophy", "humor"])

    quotes = get_quotes_by_tag(test_db, "philosophy")

    assert len(quotes) == 2
    assert all("philosophy" in q.tags for q in quotes)


def test_should_return_empty_list_when_tag_not_found(test_db: Path) -> None:
    """Test that non-existent tag returns empty list."""
    add_quote(test_db, text="Quote", author="Author", tags=["tag1"])

    quotes = get_quotes_by_tag(test_db, "nonexistent")

    assert quotes == []


# Tests for search_quotes


def test_should_search_quotes_by_text_query(test_db: Path) -> None:
    """Test searching quotes by text content."""
    add_quote(test_db, text="The answer is 42", author="Douglas Adams")
    add_quote(test_db, text="Don't Panic", author="Douglas Adams")
    add_quote(test_db, text="Something else", author="Other Author")

    quotes = search_quotes(test_db, query="answer")

    assert len(quotes) == 1
    assert "answer" in quotes[0].text.lower()


def test_should_search_quotes_by_author_in_query(test_db: Path) -> None:
    """Test searching quotes by author name in query."""
    add_quote(test_db, text="Quote 1", author="Douglas Adams")
    add_quote(test_db, text="Quote 2", author="Terry Pratchett")

    quotes = search_quotes(test_db, query="Douglas")

    assert len(quotes) == 1
    assert "Douglas" in quotes[0].author


def test_should_search_quotes_case_insensitive(test_db: Path) -> None:
    """Test that search is case-insensitive."""
    add_quote(test_db, text="The Answer is 42", author="Author")

    quotes = search_quotes(test_db, query="answer")

    assert len(quotes) == 1


def test_should_filter_quotes_by_author(test_db: Path) -> None:
    """Test filtering by author."""
    add_quote(test_db, text="Quote 1", author="Douglas Adams")
    add_quote(test_db, text="Quote 2", author="Terry Pratchett")

    quotes = search_quotes(test_db, author="Douglas Adams")

    assert len(quotes) == 1
    assert quotes[0].author == "Douglas Adams"


def test_should_filter_quotes_by_author_case_insensitive(test_db: Path) -> None:
    """Test that author filter is case-insensitive."""
    add_quote(test_db, text="Quote", author="Douglas Adams")

    quotes = search_quotes(test_db, author="douglas adams")

    assert len(quotes) == 1


def test_should_filter_quotes_by_single_tag(test_db: Path) -> None:
    """Test filtering by a single tag."""
    add_quote(test_db, text="Quote 1", author="Author", tags=["philosophy"])
    add_quote(test_db, text="Quote 2", author="Author", tags=["humor"])

    quotes = search_quotes(test_db, tags=["philosophy"])

    assert len(quotes) == 1
    assert "philosophy" in quotes[0].tags


def test_should_filter_quotes_by_multiple_tags_and_logic(test_db: Path) -> None:
    """Test filtering by multiple tags (AND logic)."""
    add_quote(test_db, text="Quote 1", author="Author", tags=["philosophy"])
    add_quote(test_db, text="Quote 2", author="Author", tags=["humor"])
    add_quote(test_db, text="Quote 3", author="Author", tags=["philosophy", "humor"])

    quotes = search_quotes(test_db, tags=["philosophy", "humor"])

    assert len(quotes) == 1
    assert set(quotes[0].tags) == {"philosophy", "humor"}


def test_should_combine_query_and_filters(test_db: Path) -> None:
    """Test combining query text with filters."""
    add_quote(test_db, text="The answer is 42", author="Douglas Adams", tags=["philosophy"])
    add_quote(test_db, text="Don't Panic", author="Douglas Adams", tags=["humor"])
    add_quote(test_db, text="The answer is 43", author="Other", tags=["philosophy"])

    quotes = search_quotes(test_db, query="answer", author="Douglas Adams", tags=["philosophy"])

    assert len(quotes) == 1
    assert quotes[0].text == "The answer is 42"


def test_should_return_all_quotes_when_no_filters(test_db: Path) -> None:
    """Test that search with no filters returns all quotes."""
    add_quote(test_db, text="Quote 1", author="Author 1")
    add_quote(test_db, text="Quote 2", author="Author 2")

    quotes = search_quotes(test_db)

    assert len(quotes) == 2


# Tests for update_quote


def test_should_update_quote_text(test_db: Path) -> None:
    """Test updating quote text."""
    quote = add_quote(test_db, text="Original", author="Author")

    result = update_quote(test_db, quote.id, text="Updated")

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert updated.text == "Updated"


def test_should_update_quote_author(test_db: Path) -> None:
    """Test updating quote author."""
    quote = add_quote(test_db, text="Quote", author="Original Author")

    result = update_quote(test_db, quote.id, author="New Author")

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert updated.author == "New Author"


def test_should_update_multiple_fields(test_db: Path) -> None:
    """Test updating multiple fields at once."""
    quote = add_quote(test_db, text="Original", author="Author", source="Source1", year=2020)

    result = update_quote(test_db, quote.id, text="Updated", source="Source2", year=2021)

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert updated.text == "Updated"
    assert updated.source == "Source2"
    assert updated.year == 2021
    assert updated.author == "Author"  # Unchanged


def test_should_update_quote_tags(test_db: Path) -> None:
    """Test replacing quote tags."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1", "tag2"])

    result = update_quote(test_db, quote.id, tags=["tag3", "tag4"])

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert set(updated.tags) == {"tag3", "tag4"}


def test_should_clear_tags_when_updated_with_empty_list(test_db: Path) -> None:
    """Test clearing all tags."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1", "tag2"])

    result = update_quote(test_db, quote.id, tags=[])

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert updated.tags == []


def test_should_return_false_when_updating_nonexistent_quote(test_db: Path) -> None:
    """Test that updating non-existent quote returns False."""
    result = update_quote(test_db, 999, text="Updated")

    assert result is False


def test_should_raise_error_when_updating_with_empty_text(test_db: Path) -> None:
    """Test that updating with empty text raises error."""
    quote = add_quote(test_db, text="Original", author="Author")

    with pytest.raises(InvalidInputError):
        update_quote(test_db, quote.id, text="")


def test_should_raise_error_when_updating_with_empty_author(test_db: Path) -> None:
    """Test that updating with empty author raises error."""
    quote = add_quote(test_db, text="Quote", author="Original")

    with pytest.raises(InvalidInputError):
        update_quote(test_db, quote.id, author="")


# Tests for delete_quote


def test_should_delete_quote(test_db: Path) -> None:
    """Test deleting a quote."""
    quote = add_quote(test_db, text="Quote", author="Author")

    result = delete_quote(test_db, quote.id)

    assert result is True
    assert get_quote_by_id(test_db, quote.id) is None


def test_should_return_false_when_deleting_nonexistent_quote(test_db: Path) -> None:
    """Test that deleting non-existent quote returns False."""
    result = delete_quote(test_db, 999)

    assert result is False


def test_should_cascade_delete_quote_tags(test_db: Path) -> None:
    """Test that deleting quote also removes tag associations."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1"])

    delete_quote(test_db, quote.id)

    # Tag should still exist but not be associated
    tags = list_all_tags(test_db)
    assert ("tag1", 0) in tags  # Tag exists but has 0 quotes


# Tests for add_tag_to_quote


def test_should_add_tag_to_quote(test_db: Path) -> None:
    """Test adding a tag to an existing quote."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1"])

    result = add_tag_to_quote(test_db, quote.id, "tag2")

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert set(updated.tags) == {"tag1", "tag2"}


def test_should_create_new_tag_when_adding_to_quote(test_db: Path) -> None:
    """Test that new tags are created automatically."""
    quote = add_quote(test_db, text="Quote", author="Author")

    result = add_tag_to_quote(test_db, quote.id, "new_tag")

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert "new_tag" in updated.tags


def test_should_not_duplicate_tag_on_quote(test_db: Path) -> None:
    """Test that adding existing tag doesn't duplicate it."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1"])

    result = add_tag_to_quote(test_db, quote.id, "tag1")

    assert result is True
    updated = get_quote_by_id(test_db, quote.id)
    assert updated.tags == ["tag1"]  # No duplicate


def test_should_return_false_when_adding_tag_to_nonexistent_quote(test_db: Path) -> None:
    """Test that adding tag to non-existent quote returns False."""
    result = add_tag_to_quote(test_db, 999, "tag")

    assert result is False


def test_should_raise_error_when_adding_empty_tag(test_db: Path) -> None:
    """Test that adding empty tag raises error."""
    quote = add_quote(test_db, text="Quote", author="Author")

    with pytest.raises(InvalidInputError):
        add_tag_to_quote(test_db, quote.id, "")


# Tests for list_all_tags


def test_should_list_all_tags_with_counts(test_db: Path) -> None:
    """Test listing all tags with usage counts."""
    add_quote(test_db, text="Quote 1", author="Author", tags=["philosophy"])
    add_quote(test_db, text="Quote 2", author="Author", tags=["humor"])
    add_quote(test_db, text="Quote 3", author="Author", tags=["philosophy", "humor"])

    tags = list_all_tags(test_db)

    assert len(tags) == 2
    assert ("humor", 2) in tags
    assert ("philosophy", 2) in tags


def test_should_return_empty_list_when_no_tags(test_db: Path) -> None:
    """Test that no tags returns empty list."""
    tags = list_all_tags(test_db)

    assert tags == []


def test_should_include_tags_with_zero_count(test_db: Path) -> None:
    """Test that orphaned tags (no quotes) are included with count 0."""
    quote = add_quote(test_db, text="Quote", author="Author", tags=["tag1"])
    delete_quote(test_db, quote.id)

    tags = list_all_tags(test_db)

    assert ("tag1", 0) in tags


# Tests for get_random_quote


def test_should_get_random_quote(test_db: Path) -> None:
    """Test getting a random quote."""
    add_quote(test_db, text="Quote 1", author="Author")
    add_quote(test_db, text="Quote 2", author="Author")

    quote = get_random_quote(test_db)

    assert quote is not None
    assert quote.text in ["Quote 1", "Quote 2"]


def test_should_return_none_when_no_quotes_for_random(test_db: Path) -> None:
    """Test that empty database returns None for random."""
    quote = get_random_quote(test_db)

    assert quote is None


def test_should_get_random_quote_filtered_by_tag(test_db: Path) -> None:
    """Test getting random quote filtered by tag."""
    add_quote(test_db, text="Quote 1", author="Author", tags=["philosophy"])
    add_quote(test_db, text="Quote 2", author="Author", tags=["humor"])
    add_quote(test_db, text="Quote 3", author="Author", tags=["philosophy"])

    # Run multiple times to increase confidence
    for _ in range(5):
        quote = get_random_quote(test_db, tag="philosophy")
        assert quote is not None
        assert "philosophy" in quote.tags


def test_should_return_none_when_no_quotes_with_tag(test_db: Path) -> None:
    """Test that non-existent tag returns None for random."""
    add_quote(test_db, text="Quote", author="Author", tags=["tag1"])

    quote = get_random_quote(test_db, tag="nonexistent")

    assert quote is None


# Tests for get_statistics


def test_should_get_statistics_for_populated_database(test_db: Path) -> None:
    """Test statistics with data."""
    add_quote(test_db, text="Quote 1", author="Douglas Adams", tags=["philosophy"])
    add_quote(test_db, text="Quote 2", author="Douglas Adams", tags=["humor"])
    add_quote(test_db, text="Quote 3", author="Terry Pratchett", tags=["philosophy"])

    stats = get_statistics(test_db)

    assert stats["total_quotes"] == 3
    assert stats["total_authors"] == 2
    assert stats["total_tags"] == 2
    assert stats["most_quoted_author"] == "Douglas Adams (2 quotes)"
    assert stats["most_common_tag"] == "philosophy (2 quotes)"


def test_should_get_statistics_for_empty_database(test_db: Path) -> None:
    """Test statistics with no data."""
    stats = get_statistics(test_db)

    assert stats["total_quotes"] == 0
    assert stats["total_authors"] == 0
    assert stats["total_tags"] == 0
    assert stats["most_quoted_author"] == "N/A"
    assert stats["most_common_tag"] == "N/A"


def test_should_handle_tie_in_most_quoted_author(test_db: Path) -> None:
    """Test that ties are handled (returns one of them)."""
    add_quote(test_db, text="Quote 1", author="Author 1")
    add_quote(test_db, text="Quote 2", author="Author 2")

    stats = get_statistics(test_db)

    assert stats["most_quoted_author"] in ["Author 1 (1 quotes)", "Author 2 (1 quotes)"]
