"""Tests for data models."""

from datetime import datetime

from mcp_theanswer.database.models import Quote, Tag


def test_should_create_quote_with_all_fields() -> None:
    """Test creating a Quote with all fields populated."""
    quote = Quote(
        id=1,
        text="The answer is 42",
        author="Deep Thought",
        source="Hitchhiker's Guide",
        year=1979,
        created_at="2024-01-01T00:00:00",
        tags=["philosophy", "humor"],
    )

    assert quote.id == 1
    assert quote.text == "The answer is 42"
    assert quote.author == "Deep Thought"
    assert quote.source == "Hitchhiker's Guide"
    assert quote.year == 1979
    assert quote.created_at == "2024-01-01T00:00:00"
    assert quote.tags == ["philosophy", "humor"]


def test_should_create_quote_with_minimal_fields() -> None:
    """Test creating a Quote with only required fields."""
    quote = Quote(id=1, text="Test quote", author="Test Author")

    assert quote.id == 1
    assert quote.text == "Test quote"
    assert quote.author == "Test Author"
    assert quote.source is None
    assert quote.year is None
    assert quote.created_at == ""
    assert quote.tags is None


def test_should_convert_quote_to_dict() -> None:
    """Test Quote.to_dict() serialization."""
    quote = Quote(
        id=42,
        text="Don't Panic",
        author="Douglas Adams",
        source="Hitchhiker's Guide",
        year=1979,
        created_at="2024-01-01T12:00:00",
        tags=["humor", "life"],
    )

    result = quote.to_dict()

    assert result == {
        "id": 42,
        "text": "Don't Panic",
        "author": "Douglas Adams",
        "source": "Hitchhiker's Guide",
        "year": 1979,
        "created_at": "2024-01-01T12:00:00",
        "tags": ["humor", "life"],
    }


def test_should_convert_quote_with_none_tags_to_dict() -> None:
    """Test Quote.to_dict() with None tags returns empty list."""
    quote = Quote(id=1, text="Test", author="Author", tags=None)

    result = quote.to_dict()

    assert result["tags"] == []


def test_should_create_quote_from_database_row() -> None:
    """Test Quote.from_row() creates Quote from database tuple."""
    row = (1, "Test quote", "Author", "Source", 2020, "2024-01-01T00:00:00")
    tags = ["tag1", "tag2"]

    quote = Quote.from_row(row, tags)

    assert quote.id == 1
    assert quote.text == "Test quote"
    assert quote.author == "Author"
    assert quote.source == "Source"
    assert quote.year == 2020
    assert quote.created_at == "2024-01-01T00:00:00"
    assert quote.tags == ["tag1", "tag2"]


def test_should_create_quote_from_row_without_tags() -> None:
    """Test Quote.from_row() with no tags provided."""
    row = (1, "Test quote", "Author", None, None, "2024-01-01T00:00:00")

    quote = Quote.from_row(row)

    assert quote.id == 1
    assert quote.tags == []


def test_should_create_quote_from_row_with_none_created_at() -> None:
    """Test Quote.from_row() handles None created_at."""
    row = (1, "Test quote", "Author", None, None, None)

    quote = Quote.from_row(row)

    assert quote.id == 1
    # Should have some timestamp, not None
    assert quote.created_at
    # Should be valid ISO format
    datetime.fromisoformat(quote.created_at)


def test_should_create_tag_with_all_fields() -> None:
    """Test creating a Tag with all fields."""
    tag = Tag(id=1, name="philosophy", count=10)

    assert tag.id == 1
    assert tag.name == "philosophy"
    assert tag.count == 10


def test_should_create_tag_with_default_count() -> None:
    """Test creating a Tag with default count."""
    tag = Tag(id=1, name="humor")

    assert tag.id == 1
    assert tag.name == "humor"
    assert tag.count == 0


def test_should_convert_tag_to_dict() -> None:
    """Test Tag.to_dict() serialization."""
    tag = Tag(id=5, name="technology", count=15)

    result = tag.to_dict()

    assert result == {"id": 5, "name": "technology", "count": 15}


def test_should_create_tag_from_database_row_with_count() -> None:
    """Test Tag.from_row() with count."""
    row = (1, "philosophy", 42)

    tag = Tag.from_row(row)

    assert tag.id == 1
    assert tag.name == "philosophy"
    assert tag.count == 42


def test_should_create_tag_from_database_row_without_count() -> None:
    """Test Tag.from_row() without count (defaults to 0)."""
    row = (2, "humor")

    tag = Tag.from_row(row)

    assert tag.id == 2
    assert tag.name == "humor"
    assert tag.count == 0
