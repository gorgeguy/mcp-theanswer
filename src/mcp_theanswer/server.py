"""MCP server entry point for Quote Vault."""

import logging
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_theanswer.config import get_auto_seed, get_database_path, get_log_level
from mcp_theanswer.database.schema import check_if_seeded, init_database
from mcp_theanswer.mcp.resources import register_resources
from mcp_theanswer.mcp.tools import register_tools
from mcp_theanswer.seed_data import seed_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP servers log to stderr
)
logger = logging.getLogger("quote-vault")


def setup_database() -> Path:
    """
    Initialize the database and optionally seed it.

    Returns:
        Path: Path to the database file

    Raises:
        Exception: If database setup fails
    """
    db_path = get_database_path()
    auto_seed = get_auto_seed()
    log_level = get_log_level()

    # Update log level from config
    logger.setLevel(log_level)

    logger.info(f"Database path: {db_path}")
    logger.info(f"Auto-seed enabled: {auto_seed}")

    # Initialize database schema
    try:
        init_database(db_path)
        logger.info("Database schema initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Check if seeding is needed
    is_seeded = check_if_seeded(db_path)
    logger.info(f"Database seeded: {is_seeded}")

    # Auto-seed if enabled and not already seeded
    if auto_seed and not is_seeded:
        try:
            logger.info("Seeding database with Douglas Adams quotes...")
            added, total = seed_database(db_path)
            logger.info(f"Database seeded: {added} quotes added, {total} total quotes")
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            # Don't fail if seeding fails - server can still run
            logger.warning("Continuing without seed data")

    return db_path


async def main() -> None:
    """
    Main entry point for the Quote Vault MCP server.

    Initializes the database, sets up the MCP server with tools,
    resources, and prompts, and runs the server.
    """
    logger.info("Starting Quote Vault MCP Server...")

    # Setup database
    try:
        db_path = setup_database()
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

    # Create MCP server instance
    server = Server("quote-vault")

    logger.info(f"Server initialized with database at {db_path}")

    # Register tools (Phase 6)
    register_tools(server, db_path)
    logger.info("Tools registered")

    # Register resources (Phase 7)
    register_resources(server, db_path)
    logger.info("Resources registered")

    # TODO: Register prompts (Phase 8)

    # Run the server using stdio transport
    logger.info("Quote Vault MCP Server is ready")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run() -> None:
    """
    Synchronous entry point for running the server.

    This is the function called by the console script entry point.
    """
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
