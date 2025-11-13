# Quote Vault MCP Server

A Model Context Protocol (MCP) server for managing and retrieving inspirational quotes. Built as a demonstration of modern Python development practices and MCP integration.

## What is This?

Quote Vault is an MCP server that enables AI assistants (like Claude) to manage a personal quote collection. It provides:

- **Tools**: Add, search, update, and delete quotes
- **Resources**: Read-only access to quote collections via URIs
- **Prompts**: Guided templates for finding inspiration and analyzing quotes

The server comes pre-seeded with Douglas Adams quotes but works with any collection you build.

## What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is a standard for connecting AI models to external tools and data sources. MCP servers expose three types of primitives:

- **Tools**: Functions the AI can invoke (e.g., `add_quote`, `search_quotes`)
- **Resources**: Data the AI can read via URIs (e.g., `quote://random`)
- **Prompts**: Templates that guide the AI's behavior (e.g., `find-inspiration`)

This server works with any MCP client, including [Claude Desktop](https://claude.ai/download).

## Features

- **Full CRUD Operations**: Add, search, update, and delete quotes
- **Flexible Search**: Find quotes by text, author, or tags
- **Tag Management**: Organize quotes with multiple tags
- **Random Quotes**: Get inspiration with random quote selection
- **Rich Metadata**: Store source, year, and context for each quote
- **SQLite Database**: Reliable local storage with full-text search
- **Development Tools**: CLI test client for testing without Claude Desktop
- **Pre-seeded Data**: 20+ Douglas Adams quotes to start with

## Installation

This project requires Python 3.11+ and uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Quick Install

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/mcp-theanswer.git
cd mcp-theanswer

# Install dependencies
uv sync

# Optional: Seed the database with Douglas Adams quotes
export QUOTE_VAULT_AUTO_SEED=true
uv run python -m mcp_theanswer.server
```

## Setup with Claude Desktop

To use Quote Vault with Claude Desktop:

1. **Install the server** (see above)

2. **Configure Claude Desktop** by editing your config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add the server configuration**:

```json
{
  "mcpServers": {
    "quote-vault": {
      "command": "uv",
      "args": [
        "run",
        "--frozen",
        "--directory",
        "/absolute/path/to/mcp-theanswer",
        "python",
        "-m",
        "mcp_theanswer.server"
      ],
      "env": {
        "QUOTE_VAULT_AUTO_SEED": "true"
      }
    }
  }
}
```

4. **Restart Claude Desktop**

5. **Verify** by asking Claude: "What tools do you have access to?" You should see quote-related tools listed.

### Environment Variables

- `QUOTE_VAULT_DB_PATH`: Database file path (default: `~/.local/share/quote-vault/quotes.db`)
- `QUOTE_VAULT_AUTO_SEED`: Auto-seed with Douglas Adams quotes (default: `false`)
- `QUOTE_VAULT_LOG_LEVEL`: Logging level (default: `INFO`)

## Usage

### With Claude Desktop

Once configured, you can interact with your quotes naturally:

```
You: "Add this quote: 'The Answer is 42' by Deep Thought"
Claude: [Uses add_quote tool to save it]

You: "Find me some inspiring quotes about life"
Claude: [Uses search_quotes tool and presents results]

You: "Give me a random quote"
Claude: [Uses quote://random resource or random_quote tool]
```

### Tools Available

| Tool            | Description                                               |
| --------------- | --------------------------------------------------------- |
| `add_quote`     | Add a new quote with text, author, source, year, and tags |
| `search_quotes` | Search quotes by text query, author, or tags              |
| `random_quote`  | Get a random quote (optionally filtered by tag)           |
| `update_quote`  | Update an existing quote's fields                         |
| `delete_quote`  | Delete a quote by ID                                      |
| `add_tag`       | Add a tag to an existing quote                            |
| `list_tags`     | List all tags with usage counts                           |

### Resources Available

| URI                       | Description                    |
| ------------------------- | ------------------------------ |
| `quote://all`             | All quotes in the vault        |
| `quote://id/{id}`         | Specific quote by ID           |
| `quote://author/{author}` | All quotes by an author        |
| `quote://tag/{tag}`       | All quotes with a specific tag |
| `quote://random`          | Random quote from collection   |
| `quote://stats`           | Collection statistics          |
| `quote://tags`            | All tags with counts           |

### Prompts Available

| Prompt             | Description                                  |
| ------------------ | -------------------------------------------- |
| `find-inspiration` | Find relevant quotes for your situation      |
| `quote-explainer`  | Analyze and explain a quote's deeper meaning |
| `add-quote-helper` | Guide through adding a well-structured quote |

## Development

### Development Test Client

Test the MCP server without Claude Desktop using the included CLI client:

```bash
# List all available tools
python scripts/test_client.py list-tools

# List all resources
python scripts/test_client.py list-resources

# List all prompts
python scripts/test_client.py list-prompts

# Add a quote
python scripts/test_client.py tool add_quote '{
  "text": "The Answer is 42",
  "author": "Deep Thought",
  "tags": ["humor", "philosophy"]
}'

# Search for quotes
python scripts/test_client.py tool search_quotes '{
  "query": "life",
  "author": "Douglas Adams"
}'

# Get a random quote
python scripts/test_client.py resource quote://random

# Get collection statistics
python scripts/test_client.py resource quote://stats

# Use a prompt
python scripts/test_client.py prompt find-inspiration '{
  "situation": "feeling overwhelmed"
}'
```

### Running Tests

```bash
# Run all tests with coverage (89% coverage)
uv run --frozen pytest

# Run specific test file
uv run --frozen pytest tests/test_tools.py

# Run with verbose output
uv run --frozen pytest -v

# Generate HTML coverage report
uv run --frozen pytest --cov-report=html
```

### Code Quality

```bash
# Format code with ruff
uv run --frozen ruff format .

# Lint code
uv run --frozen ruff check .

# Fix linting issues automatically
uv run --frozen ruff check . --fix

# Type check with pyright
uv run --frozen pyright

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Project Structure

```
mcp-theanswer/
├── src/mcp_theanswer/
│   ├── __init__.py
│   ├── main.py                 # Legacy CLI (returns 42)
│   ├── server.py               # MCP server entry point
│   ├── config.py               # Environment configuration
│   ├── seed_data.py            # Douglas Adams quotes seed data
│   ├── database/
│   │   ├── models.py           # Quote and Tag data models
│   │   ├── operations.py       # Database CRUD operations
│   │   └── schema.py           # SQLite schema and migrations
│   └── mcp/
│       ├── tools.py            # MCP tool implementations
│       ├── resources.py        # MCP resource implementations
│       └── prompts.py          # MCP prompt templates
├── scripts/
│   └── test_client.py          # Development test client
├── tests/
│   ├── test_database.py        # Database operation tests
│   ├── test_tools.py           # MCP tool tests
│   ├── test_resources.py       # MCP resource tests
│   ├── test_prompts.py         # MCP prompt tests
│   ├── test_schema.py          # Database schema tests
│   ├── test_seed_data.py       # Seed data tests
│   └── test_server.py          # Server initialization tests
├── DESIGN.md                   # Detailed design document
├── IMPLEMENTATION.md           # Implementation phases and plan
├── CLAUDE.md                   # Claude Code development guide
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

### Architecture

The Quote Vault MCP server is built in layers:

1. **Database Layer** (`database/`): SQLite database with Quote and Tag models
2. **MCP Layer** (`mcp/`): Tools, Resources, and Prompts implementations
3. **Server Layer** (`server.py`): MCP server initialization and stdio transport
4. **Configuration** (`config.py`): Environment-based configuration

The server uses:

- **SQLite** for reliable local storage
- **MCP Python SDK** for protocol implementation
- **stdio transport** for communication with MCP clients
- **Async/await** throughout for non-blocking operations

### Database Schema

**quotes** table:

- `id`: Integer primary key
- `text`: Quote text (required)
- `author`: Author name (required)
- `source`: Source/book/context (optional)
- `year`: Publication year (optional)
- `created_at`: Timestamp

**tags** table:

- `id`: Integer primary key
- `name`: Tag name (unique)

**quote_tags** junction table:

- Links quotes to tags (many-to-many)
- Cascade deletes when quote is deleted

## Troubleshooting

### Claude Desktop doesn't see the server

1. Check the config file path is correct
2. Verify the absolute path to the project is correct
3. Restart Claude Desktop completely
4. Check Claude Desktop's logs: `~/Library/Logs/Claude/` (macOS)

### Database not seeding

1. Ensure `QUOTE_VAULT_AUTO_SEED=true` is set in the environment
2. Check database file permissions
3. Verify the database hasn't already been seeded (seed only runs once)
4. Check server logs for errors

### Test client can't connect

1. Verify you're running from the project root directory
2. Check that `uv` is installed and in PATH
3. Ensure dependencies are installed: `uv sync`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests and quality checks: `uv run --frozen pytest && uv run --frozen ruff check .`
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Future Enhancements

Ideas for future versions (out of scope for v1):

- Import/export (JSON, CSV, Markdown)
- Backup and restore functionality
- Full-text search with ranking
- Quote collections/playlists
- Export quotes as images
- Web UI for browsing
- Favorite/rating system
- Full-featured CLI for end users

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast dependency management
- Uses [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) for protocol implementation
- Code quality with [ruff](https://github.com/astral-sh/ruff)
- Testing with [pytest](https://pytest.org/)
- Inspired by Douglas Adams and _The Hitchhiker's Guide to the Galaxy_

## Learn More

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [Claude Desktop](https://claude.ai/download)
- [Design Document](DESIGN.md) - Detailed architectural decisions
- [Implementation Guide](IMPLEMENTATION.md) - Phase-by-phase development plan
