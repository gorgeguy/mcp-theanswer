"""MCP tool implementations for Quote Vault."""

import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool

from mcp_theanswer.database.operations import (
    InvalidInputError,
)
from mcp_theanswer.database.operations import (
    add_quote as db_add_quote,
)
from mcp_theanswer.database.operations import (
    add_tag_to_quote as db_add_tag_to_quote,
)
from mcp_theanswer.database.operations import (
    delete_quote as db_delete_quote,
)
from mcp_theanswer.database.operations import (
    get_random_quote as db_get_random_quote,
)
from mcp_theanswer.database.operations import (
    list_all_tags as db_list_all_tags,
)
from mcp_theanswer.database.operations import (
    search_quotes as db_search_quotes,
)
from mcp_theanswer.database.operations import (
    update_quote as db_update_quote,
)

logger = logging.getLogger("quote-vault")


def register_tools(server: Server, db_path: Path) -> None:
    """
    Register all MCP tools with the server.

    Args:
        server: MCP server instance
        db_path: Path to the database file
    """

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
        """Handle tool calls."""
        logger.info(f"Tool called: {name} with arguments: {arguments}")

        try:
            if name == "add_quote":
                return await handle_add_quote(db_path, arguments)
            elif name == "search_quotes":
                return await handle_search_quotes(db_path, arguments)
            elif name == "random_quote":
                return await handle_random_quote(db_path, arguments)
            elif name == "update_quote":
                return await handle_update_quote(db_path, arguments)
            elif name == "delete_quote":
                return await handle_delete_quote(db_path, arguments)
            elif name == "add_tag_to_quote":
                return await handle_add_tag_to_quote(db_path, arguments)
            elif name == "list_tags":
                return await handle_list_tags(db_path, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            raise

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="add_quote",
                description="Add a new quote to the vault",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The quote text"},
                        "author": {"type": "string", "description": "Author name"},
                        "source": {
                            "type": "string",
                            "description": "Source (book, speech, etc.)",
                        },
                        "year": {"type": "integer", "description": "Year published/said"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Associated tags",
                        },
                    },
                    "required": ["text", "author"],
                },
            ),
            Tool(
                name="search_quotes",
                description="Search for quotes using substring matching",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search text (searches text and author)",
                        },
                        "author": {"type": "string", "description": "Filter by author"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags (quote must have ALL tags)",
                        },
                    },
                },
            ),
            Tool(
                name="random_quote",
                description="Get a random quote, optionally filtered by tag",
                inputSchema={
                    "type": "object",
                    "properties": {"tag": {"type": "string", "description": "Optional tag filter"}},
                },
            ),
            Tool(
                name="update_quote",
                description="Update an existing quote",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Quote ID"},
                        "text": {"type": "string", "description": "Updated quote text"},
                        "author": {"type": "string", "description": "Updated author name"},
                        "source": {"type": "string", "description": "Updated source"},
                        "year": {"type": "integer", "description": "Updated year"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Updated tags (replaces all existing)",
                        },
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="delete_quote",
                description="Delete a quote by ID",
                inputSchema={
                    "type": "object",
                    "properties": {"id": {"type": "integer", "description": "Quote ID"}},
                    "required": ["id"],
                },
            ),
            Tool(
                name="add_tag_to_quote",
                description="Add a tag to an existing quote",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "quote_id": {"type": "integer", "description": "Quote ID"},
                        "tag": {"type": "string", "description": "Tag name to add"},
                    },
                    "required": ["quote_id", "tag"],
                },
            ),
            Tool(
                name="list_tags",
                description="List all unique tags in the system with usage counts",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]


async def handle_add_quote(db_path: Path, arguments: dict[str, Any]) -> list[Any]:
    """Handle add_quote tool call."""
    try:
        quote = db_add_quote(
            db_path,
            text=arguments["text"],
            author=arguments["author"],
            source=arguments.get("source"),
            year=arguments.get("year"),
            tags=arguments.get("tags"),
        )

        return [
            {
                "type": "text",
                "text": f"Quote added successfully with ID {quote.id}\n\n"
                f'"{quote.text}"\n— {quote.author}',
            }
        ]
    except InvalidInputError as e:
        return [{"type": "text", "text": f"Error: {e}"}]


async def handle_search_quotes(db_path: Path, arguments: dict[str, Any]) -> list[Any]:
    """Handle search_quotes tool call."""
    quotes = db_search_quotes(
        db_path,
        query=arguments.get("query"),
        author=arguments.get("author"),
        tags=arguments.get("tags"),
    )

    if not quotes:
        return [{"type": "text", "text": "No quotes found matching your search criteria."}]

    # Format results
    result_lines = [f"Found {len(quotes)} quote(s):\n"]
    for quote in quotes:
        result_lines.append(f'[{quote.id}] "{quote.text}"')
        result_lines.append(f"    — {quote.author}")
        if quote.source:
            source_info = quote.source
            if quote.year:
                source_info += f" ({quote.year})"
            result_lines.append(f"    Source: {source_info}")
        if quote.tags:
            result_lines.append(f"    Tags: {', '.join(quote.tags)}")
        result_lines.append("")

    return [{"type": "text", "text": "\n".join(result_lines)}]


async def handle_random_quote(db_path: Path, arguments: dict[str, Any]) -> list[Any]:
    """Handle random_quote tool call."""
    quote = db_get_random_quote(db_path, tag=arguments.get("tag"))

    if not quote:
        tag_msg = f" with tag '{arguments.get('tag')}'" if arguments.get("tag") else ""
        return [{"type": "text", "text": f"No quotes found{tag_msg}."}]

    # Format quote
    lines = [f'"{quote.text}"', f"— {quote.author}"]
    if quote.source:
        source_info = quote.source
        if quote.year:
            source_info += f" ({quote.year})"
        lines.append(f"\nSource: {source_info}")
    if quote.tags:
        lines.append(f"Tags: {', '.join(quote.tags)}")
    lines.append(f"\n[Quote ID: {quote.id}]")

    return [{"type": "text", "text": "\n".join(lines)}]


async def handle_update_quote(db_path: Path, arguments: dict[str, Any]) -> list[Any]:
    """Handle update_quote tool call."""
    try:
        quote_id = arguments["id"]

        # Build update kwargs
        update_kwargs = {}
        for field in ["text", "author", "source", "year", "tags"]:
            if field in arguments:
                update_kwargs[field] = arguments[field]

        if not update_kwargs:
            return [{"type": "text", "text": "Error: No fields specified for update"}]

        success = db_update_quote(db_path, quote_id, **update_kwargs)

        if not success:
            return [{"type": "text", "text": f"Error: Quote with ID {quote_id} not found"}]

        return [{"type": "text", "text": f"Quote {quote_id} updated successfully"}]
    except InvalidInputError as e:
        return [{"type": "text", "text": f"Error: {e}"}]


async def handle_delete_quote(db_path: Path, arguments: dict[str, Any]) -> list[Any]:
    """Handle delete_quote tool call."""
    quote_id = arguments["id"]
    success = db_delete_quote(db_path, quote_id)

    if not success:
        return [{"type": "text", "text": f"Error: Quote with ID {quote_id} not found"}]

    return [{"type": "text", "text": f"Quote {quote_id} deleted successfully"}]


async def handle_add_tag_to_quote(db_path: Path, arguments: dict[str, Any]) -> list[Any]:
    """Handle add_tag_to_quote tool call."""
    try:
        quote_id = arguments["quote_id"]
        tag = arguments["tag"]

        success = db_add_tag_to_quote(db_path, quote_id, tag)

        if not success:
            return [{"type": "text", "text": f"Error: Quote with ID {quote_id} not found"}]

        return [{"type": "text", "text": f"Tag '{tag}' added to quote {quote_id} successfully"}]
    except InvalidInputError as e:
        return [{"type": "text", "text": f"Error: {e}"}]


async def handle_list_tags(db_path: Path, _arguments: dict[str, Any]) -> list[Any]:
    """Handle list_tags tool call."""
    tags = db_list_all_tags(db_path)

    if not tags:
        return [{"type": "text", "text": "No tags found in the system."}]

    # Format results
    lines = [f"Found {len(tags)} tag(s):\n"]
    for tag_name, count in tags:
        lines.append(f"  • {tag_name}: {count} quote(s)")

    return [{"type": "text", "text": "\n".join(lines)}]
