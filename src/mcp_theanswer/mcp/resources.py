"""MCP resource implementations for Quote Vault."""

import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from mcp.server import Server
from mcp.types import Resource

from mcp_theanswer.database.models import Quote
from mcp_theanswer.database.operations import (
    get_all_quotes,
    get_quote_by_id,
    get_random_quote,
    list_all_tags,
    search_quotes,
)

logger = logging.getLogger("quote-vault")


def _quote_to_dict(quote: Quote) -> dict[str, Any]:
    """
    Convert a Quote object to a dictionary for JSON serialization.

    Args:
        quote: Quote object to convert

    Returns:
        dict[str, Any]: Quote data as dictionary
    """
    return {
        "id": quote.id,
        "text": quote.text,
        "author": quote.author,
        "source": quote.source,
        "year": quote.year,
        "tags": quote.tags,
    }


def _get_stats(db_path: Path) -> dict[str, Any]:
    """
    Calculate statistics about the quote collection.

    Args:
        db_path: Path to the database file

    Returns:
        dict[str, Any]: Statistics dictionary
    """
    quotes = get_all_quotes(db_path)
    tags = list_all_tags(db_path)

    # Count total quotes
    total_quotes = len(quotes)

    # Count unique authors
    authors = [q.author for q in quotes]
    total_authors = len(set(authors))

    # Count total tags
    total_tags = len(tags)

    # Find most quoted author
    author_counts: dict[str, int] = {}
    for author in authors:
        author_counts[author] = author_counts.get(author, 0) + 1

    most_quoted_author = "N/A"
    if author_counts:
        top_author = max(author_counts.items(), key=lambda x: x[1])
        most_quoted_author = f"{top_author[0]} ({top_author[1]} quotes)"

    # Find most common tag
    most_common_tag = "N/A"
    if tags:
        top_tag = max(tags, key=lambda x: x[1])
        most_common_tag = f"{top_tag[0]} ({top_tag[1]} quotes)"

    return {
        "total_quotes": total_quotes,
        "total_authors": total_authors,
        "total_tags": total_tags,
        "most_quoted_author": most_quoted_author,
        "most_common_tag": most_common_tag,
    }


async def get_resource_list() -> list[Resource]:
    """
    Get list of all available resources.

    Returns:
        list[Resource]: List of resource descriptors
    """
    return [
        Resource(
            uri="quote://all",
            name="All Quotes",
            description="Returns all quotes in the vault",
            mimeType="application/json",
        ),
        Resource(
            uri="quote://id/{id}",
            name="Quote by ID",
            description="Returns a specific quote by ID",
            mimeType="application/json",
        ),
        Resource(
            uri="quote://author/{author}",
            name="Quotes by Author",
            description="Returns all quotes by a specific author",
            mimeType="application/json",
        ),
        Resource(
            uri="quote://tag/{tag}",
            name="Quotes by Tag",
            description="Returns all quotes with a specific tag",
            mimeType="application/json",
        ),
        Resource(
            uri="quote://random",
            name="Random Quote",
            description="Returns a random quote from the collection",
            mimeType="application/json",
        ),
        Resource(
            uri="quote://stats",
            name="Collection Statistics",
            description="Returns statistics about the quote collection",
            mimeType="application/json",
        ),
        Resource(
            uri="quote://tags",
            name="All Tags",
            description="Returns all available tags with counts",
            mimeType="application/json",
        ),
    ]


async def read_resource_content(uri: str, db_path: Path) -> str:
    """
    Read a resource by URI.

    Args:
        uri: Resource URI
        db_path: Path to the database file

    Returns:
        str: Resource content as JSON string

    Raises:
        ValueError: If URI is invalid or resource not found
    """
    logger.info(f"Resource requested: {uri}")

    # Handle quote://all
    if uri == "quote://all":
        quotes = get_all_quotes(db_path)
        data = [_quote_to_dict(q) for q in quotes]
        return json.dumps(data, indent=2)

    # Handle quote://id/{id}
    if uri.startswith("quote://id/"):
        quote_id_str = uri[len("quote://id/") :]
        try:
            quote_id = int(quote_id_str)
        except ValueError as e:
            raise ValueError(f"Invalid quote ID: {quote_id_str}") from e

        quote = get_quote_by_id(db_path, quote_id)
        if not quote:
            raise ValueError(f"Quote not found: {quote_id}")

        return json.dumps(_quote_to_dict(quote), indent=2)

    # Handle quote://author/{author}
    if uri.startswith("quote://author/"):
        author = unquote(uri[len("quote://author/") :])
        quotes = search_quotes(db_path, author=author)
        data = [_quote_to_dict(q) for q in quotes]
        return json.dumps(data, indent=2)

    # Handle quote://tag/{tag}
    if uri.startswith("quote://tag/"):
        tag = unquote(uri[len("quote://tag/") :])
        quotes = search_quotes(db_path, tags=[tag])
        data = [_quote_to_dict(q) for q in quotes]
        return json.dumps(data, indent=2)

    # Handle quote://random
    if uri == "quote://random":
        quote = get_random_quote(db_path)
        if not quote:
            return json.dumps({"error": "No quotes available"}, indent=2)
        return json.dumps(_quote_to_dict(quote), indent=2)

    # Handle quote://stats
    if uri == "quote://stats":
        stats = _get_stats(db_path)
        return json.dumps(stats, indent=2)

    # Handle quote://tags
    if uri == "quote://tags":
        tags = list_all_tags(db_path)
        data = [{"name": name, "count": count} for name, count in tags]
        return json.dumps(data, indent=2)

    # Unknown resource
    raise ValueError(f"Unknown resource URI: {uri}")


def register_resources(server: Server, db_path: Path) -> None:
    """
    Register all MCP resources with the server.

    Args:
        server: MCP server instance
        db_path: Path to the database file
    """

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List all available resources."""
        return await get_resource_list()

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI."""
        return await read_resource_content(uri, db_path)
