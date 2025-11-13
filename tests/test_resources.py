"""Tests for MCP resources."""

import json
import tempfile
from pathlib import Path
from urllib.parse import quote

import pytest

from mcp_theanswer.database.operations import add_quote
from mcp_theanswer.database.schema import init_database
from mcp_theanswer.mcp.resources import (
    _get_stats,
    _quote_to_dict,
    get_resource_list,
    read_resource_content,
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


# Tests for helper functions


def test_should_convert_quote_to_dict(seeded_db: Path) -> None:
    """Test converting Quote object to dictionary."""
    from mcp_theanswer.database.operations import get_quote_by_id

    quote = get_quote_by_id(seeded_db, 1)
    assert quote is not None

    result = _quote_to_dict(quote)

    assert result["id"] == 1
    assert result["text"] == "The answer is 42"
    assert result["author"] == "Douglas Adams"
    assert result["source"] == "Hitchhiker's Guide"
    assert result["year"] == 1979
    assert set(result["tags"]) == {"philosophy", "humor"}


def test_should_calculate_stats_for_populated_database(seeded_db: Path) -> None:
    """Test calculating statistics for a database with quotes."""
    stats = _get_stats(seeded_db)

    assert stats["total_quotes"] == 3
    assert stats["total_authors"] == 2
    assert stats["total_tags"] == 4
    assert "Douglas Adams" in stats["most_quoted_author"]
    assert "2 quotes" in stats["most_quoted_author"]
    # Either humor or philosophy could be most common (both have 2)
    assert "2 quotes" in stats["most_common_tag"]


def test_should_handle_empty_database_stats(temp_db: Path) -> None:
    """Test calculating statistics for an empty database."""
    stats = _get_stats(temp_db)

    assert stats["total_quotes"] == 0
    assert stats["total_authors"] == 0
    assert stats["total_tags"] == 0
    assert stats["most_quoted_author"] == "N/A"
    assert stats["most_common_tag"] == "N/A"


# Tests for resource URIs (integration tests would test the full MCP flow)
# These tests verify the logic within read_resource handler


@pytest.mark.asyncio
async def test_should_list_all_resources() -> None:
    """Test listing all available resources."""
    resources = await get_resource_list()

    assert len(resources) == 7

    # Check URIs (AnyUrl objects may URL-encode special characters)
    uris = [str(r.uri) for r in resources]
    assert "quote://all" in uris
    # Curly braces get URL-encoded: {id} becomes %7Bid%7D
    assert any("quote://id/" in uri for uri in uris)
    assert any("quote://author/" in uri for uri in uris)
    assert any("quote://tag/" in uri for uri in uris)
    assert "quote://random" in uris
    assert "quote://stats" in uris
    assert "quote://tags" in uris

    # Check all have JSON mime type
    for resource in resources:
        assert resource.mimeType == "application/json"


@pytest.mark.asyncio
async def test_should_read_all_quotes_resource(seeded_db: Path) -> None:
    """Test reading quote://all resource."""
    result = await read_resource_content("quote://all", seeded_db)

    data = json.loads(result)
    assert len(data) == 3
    assert all("id" in q for q in data)
    assert all("text" in q for q in data)
    assert all("author" in q for q in data)


@pytest.mark.asyncio
async def test_should_read_quote_by_id_resource(seeded_db: Path) -> None:
    """Test reading quote://id/{id} resource."""
    result = await read_resource_content("quote://id/1", seeded_db)
    data = json.loads(result)

    assert data["id"] == 1
    assert data["text"] == "The answer is 42"
    assert data["author"] == "Douglas Adams"


@pytest.mark.asyncio
async def test_should_handle_invalid_quote_id(seeded_db: Path) -> None:
    """Test reading quote with invalid ID."""
    with pytest.raises(ValueError, match="Invalid quote ID"):
        await read_resource_content("quote://id/not-a-number", seeded_db)


@pytest.mark.asyncio
async def test_should_handle_nonexistent_quote_id(seeded_db: Path) -> None:
    """Test reading quote that doesn't exist."""
    with pytest.raises(ValueError, match="Quote not found"):
        await read_resource_content("quote://id/999", seeded_db)


@pytest.mark.asyncio
async def test_should_read_quotes_by_author_resource(seeded_db: Path) -> None:
    """Test reading quote://author/{author} resource."""
    author = "Douglas Adams"
    result = await read_resource_content(f"quote://author/{author}", seeded_db)
    data = json.loads(result)

    assert len(data) == 2
    assert all(q["author"] == "Douglas Adams" for q in data)


@pytest.mark.asyncio
async def test_should_handle_url_encoded_author_names(seeded_db: Path) -> None:
    """Test reading author resource with URL-encoded name."""
    # URL encode author name with spaces
    author_encoded = quote("Douglas Adams")
    result = await read_resource_content(f"quote://author/{author_encoded}", seeded_db)
    data = json.loads(result)

    assert len(data) == 2


@pytest.mark.asyncio
async def test_should_read_quotes_by_tag_resource(seeded_db: Path) -> None:
    """Test reading quote://tag/{tag} resource."""
    result = await read_resource_content("quote://tag/philosophy", seeded_db)
    data = json.loads(result)

    assert len(data) == 2
    assert all("philosophy" in q["tags"] for q in data)


@pytest.mark.asyncio
async def test_should_read_random_quote_resource(seeded_db: Path) -> None:
    """Test reading quote://random resource."""
    result = await read_resource_content("quote://random", seeded_db)
    data = json.loads(result)

    # Should return a single quote object
    assert "id" in data
    assert "text" in data
    assert "author" in data


@pytest.mark.asyncio
async def test_should_handle_random_quote_empty_database(temp_db: Path) -> None:
    """Test reading random quote from empty database."""
    result = await read_resource_content("quote://random", temp_db)
    data = json.loads(result)

    assert "error" in data


@pytest.mark.asyncio
async def test_should_read_stats_resource(seeded_db: Path) -> None:
    """Test reading quote://stats resource."""
    result = await read_resource_content("quote://stats", seeded_db)
    data = json.loads(result)

    assert data["total_quotes"] == 3
    assert data["total_authors"] == 2
    assert data["total_tags"] == 4
    assert "Douglas Adams" in data["most_quoted_author"]
    assert isinstance(data["most_common_tag"], str)


@pytest.mark.asyncio
async def test_should_read_tags_resource(seeded_db: Path) -> None:
    """Test reading quote://tags resource."""
    result = await read_resource_content("quote://tags", seeded_db)
    data = json.loads(result)

    assert len(data) == 4
    assert all("name" in tag for tag in data)
    assert all("count" in tag for tag in data)

    # Check specific tags exist
    tag_names = [tag["name"] for tag in data]
    assert "philosophy" in tag_names
    assert "humor" in tag_names
    assert "wisdom" in tag_names
    assert "classic" in tag_names


@pytest.mark.asyncio
async def test_should_handle_unknown_resource_uri(seeded_db: Path) -> None:
    """Test reading an unknown resource URI."""
    with pytest.raises(ValueError, match="Unknown resource URI"):
        await read_resource_content("quote://unknown", seeded_db)


@pytest.mark.asyncio
async def test_should_return_empty_array_for_nonexistent_author(seeded_db: Path) -> None:
    """Test reading quotes by author that doesn't exist."""
    result = await read_resource_content("quote://author/NonexistentAuthor", seeded_db)
    data = json.loads(result)

    assert data == []


@pytest.mark.asyncio
async def test_should_return_empty_array_for_nonexistent_tag(seeded_db: Path) -> None:
    """Test reading quotes by tag that doesn't exist."""
    result = await read_resource_content("quote://tag/nonexistent", seeded_db)
    data = json.loads(result)

    assert data == []
