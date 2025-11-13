"""Development test client for Quote Vault MCP server."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_tool(session: ClientSession, tool_name: str, args_json: str) -> None:
    """
    Invoke a tool and display the result.

    Args:
        session: MCP client session
        tool_name: Name of the tool to invoke
        args_json: JSON string of tool arguments
    """
    try:
        arguments = json.loads(args_json) if args_json else {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON arguments: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = await session.call_tool(tool_name, arguments)
        # Extract content from MCP response
        for content in result.content:
            if hasattr(content, "text"):
                # Try to parse as JSON for pretty printing
                try:
                    data = json.loads(content.text)
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    # Not JSON, just print as is
                    print(content.text)
            else:
                print(content)
    except Exception as e:
        print(f"Error invoking tool '{tool_name}': {e}", file=sys.stderr)
        sys.exit(1)


async def fetch_resource(session: ClientSession, uri: str) -> None:
    """
    Fetch a resource and display its content.

    Args:
        session: MCP client session
        uri: Resource URI to fetch
    """
    try:
        result = await session.read_resource(uri)
        for content in result.contents:
            if hasattr(content, "text"):
                # Parse JSON if it looks like JSON
                try:
                    data = json.loads(content.text)
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    # Not JSON, just print as is
                    print(content.text)
            else:
                print(content)
    except Exception as e:
        print(f"Error fetching resource '{uri}': {e}", file=sys.stderr)
        sys.exit(1)


async def get_prompt(session: ClientSession, prompt_name: str, args_json: str) -> None:
    """
    Get a prompt and display its content.

    Args:
        session: MCP client session
        prompt_name: Name of the prompt
        args_json: JSON string of prompt arguments
    """
    try:
        arguments = json.loads(args_json) if args_json else {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON arguments: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = await session.get_prompt(prompt_name, arguments)
        print(f"Description: {result.description}\n")
        print("Messages:")
        for i, msg in enumerate(result.messages, 1):
            print(f"\n--- Message {i} (role: {msg.role}) ---")
            if hasattr(msg.content, "text"):
                print(msg.content.text)
            else:
                print(msg.content)
    except Exception as e:
        print(f"Error getting prompt '{prompt_name}': {e}", file=sys.stderr)
        sys.exit(1)


async def list_tools(session: ClientSession) -> None:
    """
    List all available tools.

    Args:
        session: MCP client session
    """
    try:
        result = await session.list_tools()
        print(f"Available Tools ({len(result.tools)}):\n")
        for tool in result.tools:
            print(f"  {tool.name}")
            print(f"    Description: {tool.description}")
            if tool.inputSchema:
                print(f"    Input Schema: {json.dumps(tool.inputSchema, indent=6)}")
            print()
    except Exception as e:
        print(f"Error listing tools: {e}", file=sys.stderr)
        sys.exit(1)


async def list_resources(session: ClientSession) -> None:
    """
    List all available resources.

    Args:
        session: MCP client session
    """
    try:
        result = await session.list_resources()
        print(f"Available Resources ({len(result.resources)}):\n")
        for resource in result.resources:
            print(f"  {resource.uri}")
            print(f"    Name: {resource.name}")
            print(f"    Description: {resource.description}")
            print(f"    MIME Type: {resource.mimeType}")
            print()
    except Exception as e:
        print(f"Error listing resources: {e}", file=sys.stderr)
        sys.exit(1)


async def list_prompts(session: ClientSession) -> None:
    """
    List all available prompts.

    Args:
        session: MCP client session
    """
    try:
        result = await session.list_prompts()
        print(f"Available Prompts ({len(result.prompts)}):\n")
        for prompt in result.prompts:
            print(f"  {prompt.name}")
            print(f"    Description: {prompt.description}")
            if prompt.arguments:
                print("    Arguments:")
                for arg in prompt.arguments:
                    required = "required" if arg.required else "optional"
                    print(f"      - {arg.name} ({required}): {arg.description}")
            print()
    except Exception as e:
        print(f"Error listing prompts: {e}", file=sys.stderr)
        sys.exit(1)


async def main() -> None:
    """Main entry point for the test client."""
    parser = argparse.ArgumentParser(
        description="Development test client for Quote Vault MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all tools
  python scripts/test_client.py list-tools

  # List all resources
  python scripts/test_client.py list-resources

  # List all prompts
  python scripts/test_client.py list-prompts

  # Invoke a tool
  python scripts/test_client.py tool add_quote '{"text": "The Answer is 42", "author": "Deep Thought"}'

  # Fetch a resource
  python scripts/test_client.py resource quote://random

  # Get a prompt
  python scripts/test_client.py prompt find-inspiration '{"situation": "feeling lost"}'
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Tool command
    tool_parser = subparsers.add_parser("tool", help="Invoke a tool")
    tool_parser.add_argument("name", help="Tool name")
    tool_parser.add_argument("arguments", nargs="?", default="{}", help="JSON arguments")

    # Resource command
    resource_parser = subparsers.add_parser("resource", help="Fetch a resource")
    resource_parser.add_argument("uri", help="Resource URI")

    # Prompt command
    prompt_parser = subparsers.add_parser("prompt", help="Get a prompt")
    prompt_parser.add_argument("name", help="Prompt name")
    prompt_parser.add_argument("arguments", nargs="?", default="{}", help="JSON arguments")

    # List commands
    subparsers.add_parser("list-tools", help="List all available tools")
    subparsers.add_parser("list-resources", help="List all available resources")
    subparsers.add_parser("list-prompts", help="List all available prompts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Find the server script
    # Assume we're running from project root
    server_script = Path(__file__).parent.parent / "src" / "mcp_theanswer" / "server.py"

    if not server_script.exists():
        print(f"Error: Server script not found at {server_script}", file=sys.stderr)
        sys.exit(1)

    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "--frozen", "python", "-m", "mcp_theanswer.server"],
        env=None,
    )

    # Connect to server and run command
    async with (
        stdio_client(server_params) as (read, write),
        ClientSession(read, write) as session,
    ):
        # Initialize the session
        await session.initialize()

        # Execute the requested command
        if args.command == "tool":
            await run_tool(session, args.name, args.arguments)
        elif args.command == "resource":
            await fetch_resource(session, args.uri)
        elif args.command == "prompt":
            await get_prompt(session, args.name, args.arguments)
        elif args.command == "list-tools":
            await list_tools(session)
        elif args.command == "list-resources":
            await list_resources(session)
        elif args.command == "list-prompts":
            await list_prompts(session)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
