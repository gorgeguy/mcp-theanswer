"""Exercise real MCP v2 handler registration and protocol dispatch."""

import json
from typing import TYPE_CHECKING

import pytest
from mcp import Client
from mcp.server import Server

from mcp_theanswer.database.schema import init_database
from mcp_theanswer.mcp.prompts import register_prompts
from mcp_theanswer.mcp.resources import register_resources
from mcp_theanswer.mcp.tools import register_tools

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.asyncio
async def test_protocol_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "quotes.db"
    init_database(db)
    server = Server("test-quote-vault")
    register_tools(server, db)
    register_resources(server, db)
    register_prompts(server)

    async with Client(server) as client:
        tools = await client.list_tools()
        assert len(tools.tools) == 7
        added = await client.call_tool("add_quote", {"text": "Test quote", "author": "Test author"})
        assert not added.is_error
        resources = await client.list_resources()
        assert len(resources.resources) == 7
        result = await client.read_resource("quote://all")
        assert json.loads(result.contents[0].text)[0]["text"] == "Test quote"
        prompts = await client.list_prompts()
        assert prompts.prompts
