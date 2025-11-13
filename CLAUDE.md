# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quote Vault MCP Server** is a Model Context Protocol (MCP) server for managing and retrieving inspirational quotes. It demonstrates modern Python development practices with uv, ruff, pytest, and pre-commit hooks, while implementing all three MCP primitives: Tools, Resources, and Prompts.

The server:

- Manages a personal quote collection using SQLite
- Provides 7 tools for CRUD operations
- Exposes 7 resources for read-only data access via URIs
- Includes 3 prompts to guide LLM behavior
- Comes with 20+ Douglas Adams quotes as seed data
- Includes a development test client for testing without Claude Desktop

## Development Commands

### Testing

```bash
# Run all tests with coverage (89% coverage, 170 tests)
uv run --frozen pytest

# Run specific test file
uv run --frozen pytest tests/test_tools.py

# Run single test function
uv run --frozen pytest tests/test_tools.py::test_should_add_quote_with_all_fields

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
```

### Pre-commit Hooks

```bash
# Install hooks (one-time setup for new developers)
uv run pre-commit install

# Run all hooks manually
uv run pre-commit run --all-files

# Run hooks on staged files
uv run pre-commit run
```

### Running the MCP Server

```bash
# Run the MCP server (connects via stdio)
uv run --frozen python -m mcp_theanswer.server

# Run with auto-seed enabled
QUOTE_VAULT_AUTO_SEED=true uv run --frozen python -m mcp_theanswer.server

# Run with custom database path
QUOTE_VAULT_DB_PATH=/path/to/custom/db.sqlite uv run --frozen python -m mcp_theanswer.server
```

### Using the Development Test Client

```bash
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
```

## Project Structure

```
mcp-theanswer/
├── src/mcp_theanswer/
│   ├── __init__.py
│   ├── main.py                  # Legacy CLI (returns 42)
│   ├── server.py                # MCP server entry point (main server code)
│   ├── config.py                # Environment configuration
│   ├── seed_data.py             # Douglas Adams quotes seed data (20+ quotes)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # Quote and Tag data models
│   │   ├── operations.py        # Database CRUD operations
│   │   └── schema.py            # SQLite schema, migrations, versioning
│   └── mcp/
│       ├── __init__.py
│       ├── tools.py             # 7 MCP tool implementations
│       ├── resources.py         # 7 MCP resource implementations
│       └── prompts.py           # 3 MCP prompt template implementations
├── scripts/
│   └── test_client.py           # Development test client (CLI for testing MCP server)
├── tests/
│   ├── test_database.py         # Database operation tests (52 tests)
│   ├── test_tools.py            # MCP tool tests (38 tests)
│   ├── test_resources.py        # MCP resource tests (17 tests)
│   ├── test_prompts.py          # MCP prompt tests (14 tests)
│   ├── test_schema.py           # Database schema tests (15 tests)
│   ├── test_seed_data.py        # Seed data tests (17 tests)
│   ├── test_server.py           # Server initialization tests (11 tests)
│   ├── test_models.py           # Model tests (10 tests)
│   └── test_main.py             # Legacy main tests (2 tests)
├── DESIGN.md                    # Detailed design document
├── IMPLEMENTATION.md            # Implementation phases and plan (10 phases)
├── CLAUDE.md                    # This file
├── pyproject.toml               # Project configuration
└── README.md                    # User documentation
```

## Configuration Details

### Ruff Configuration (pyproject.toml)

- Line length: 100 characters
- Target: Python 3.11+
- Enabled linters: pycodestyle, pyflakes, isort, flake8-bugbear, flake8-comprehensions, pyupgrade, flake8-unused-arguments, flake8-simplify, flake8-type-checking, flake8-use-pathlib, Ruff-specific rules
- Test files ignore unused arguments and allow assertions

### Pytest Configuration (pyproject.toml)

- Tests automatically run with coverage reporting
- HTML coverage reports generated in `htmlcov/`
- Verbose output by default
- Coverage source: `src/mcp_theanswer`
- Current coverage: 89% (170 tests passing)
- Uses anyio for async testing

### Pre-commit Hooks (.pre-commit-config.yaml)

- Ruff formatting and linting with auto-fix
- Prettier for YAML, JSON, and Markdown
- Standard hooks: trailing whitespace, EOF fixer, YAML/JSON/TOML validation, merge conflict detection, debug statement detection

### Environment Variables

- `QUOTE_VAULT_DB_PATH`: Database file path (default: `~/.local/share/quote-vault/quotes.db`)
- `QUOTE_VAULT_AUTO_SEED`: Auto-seed with Douglas Adams quotes (default: `false`)
- `QUOTE_VAULT_LOG_LEVEL`: Logging level (default: `INFO`)

## Architecture Notes

### Layered Architecture

The Quote Vault MCP server is built in distinct layers:

1. **Database Layer** (`database/`)
   - `schema.py`: SQLite schema definition, initialization, version tracking
   - `models.py`: Quote and Tag dataclasses with serialization
   - `operations.py`: CRUD operations, search, tagging (217 lines)

2. **MCP Layer** (`mcp/`)
   - `tools.py`: 7 tools for actions (add_quote, search_quotes, random_quote, update_quote, delete_quote, add_tag, list_tags)
   - `resources.py`: 7 resources for data access (quote://all, quote://id/{id}, quote://author/{author}, quote://tag/{tag}, quote://random, quote://stats, quote://tags)
   - `prompts.py`: 3 prompts for LLM guidance (find-inspiration, quote-explainer, add-quote-helper)

3. **Server Layer** (`server.py`)
   - MCP server initialization with stdio transport
   - Database setup and optional auto-seeding
   - Registration of tools, resources, and prompts

4. **Configuration** (`config.py`)
   - Environment-based configuration with sensible defaults
   - Cross-platform database path handling

### Database Schema

**quotes** table:

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `text`: TEXT NOT NULL (the quote content)
- `author`: TEXT NOT NULL (author name)
- `source`: TEXT (book/source/context)
- `year`: INTEGER (publication year)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**tags** table:

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL UNIQUE (tag name)

**quote_tags** junction table:

- `quote_id`: INTEGER NOT NULL (foreign key to quotes.id)
- `tag_id`: INTEGER NOT NULL (foreign key to tags.id)
- PRIMARY KEY (quote_id, tag_id)
- CASCADE DELETE when quote is deleted

**schema_version** table:

- `version`: INTEGER PRIMARY KEY (schema version number)
- `applied_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Key Implementation Details

1. **MCP Communication**: Uses stdio transport (stdin/stdout) for MCP protocol
2. **Async/Await**: All MCP handlers are async functions
3. **Database**: SQLite with proper connection management and transactions
4. **Search**: Case-insensitive search with LIKE queries and tag filtering
5. **Seeding**: Idempotent seeding - only seeds once per database
6. **Error Handling**: Descriptive error messages for debugging
7. **Type Safety**: Type hints throughout, checked with pyright
8. **Testing**: Comprehensive unit and integration tests with in-memory databases

### Important Code Locations

- MCP server entry point: `src/mcp_theanswer/server.py:72` (main function)
- Database operations: `src/mcp_theanswer/database/operations.py`
- Tool registration: `src/mcp_theanswer/mcp/tools.py:296` (register_tools function)
- Resource registration: `src/mcp_theanswer/mcp/resources.py:219` (register_resources function)
- Prompt registration: `src/mcp_theanswer/mcp/prompts.py:216` (register_prompts function)
- Seed data: `src/mcp_theanswer/seed_data.py:9` (SEED_QUOTES list)
- Test client: `scripts/test_client.py:169` (main function)

## Testing Strategy

### Test Organization

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test MCP tool/resource/prompt handlers with real database operations
- **Fixture-based**: Use pytest fixtures for database setup/teardown
- **In-memory**: All tests use in-memory SQLite (`:memory:`) for speed
- **Descriptive names**: `test_should_<expected>_when_<condition>`

### Test Coverage by Module

| Module                 | Coverage | Lines | Missing |
| ---------------------- | -------- | ----- | ------- |
| database/operations.py | 100%     | 217   | 0       |
| database/models.py     | 100%     | 30    | 0       |
| database/schema.py     | 92%      | 48    | 4       |
| mcp/tools.py           | 79%      | 117   | 25      |
| mcp/resources.py       | 92%      | 80    | 6       |
| mcp/prompts.py         | 85%      | 41    | 6       |
| server.py              | 61%      | 64    | 25      |
| seed_data.py           | 89%      | 19    | 2       |

**Overall**: 89% coverage (640 statements, 69 missing)

### Running Specific Test Suites

```bash
# Database tests (52 tests)
uv run --frozen pytest tests/test_database.py -v

# MCP tools tests (38 tests)
uv run --frozen pytest tests/test_tools.py -v

# MCP resources tests (17 tests)
uv run --frozen pytest tests/test_resources.py -v

# MCP prompts tests (14 tests)
uv run --frozen pytest tests/test_prompts.py -v

# Schema tests (15 tests)
uv run --frozen pytest tests/test_schema.py -v

# Seed data tests (17 tests)
uv run --frozen pytest tests/test_seed_data.py -v

# Server tests (11 tests)
uv run --frozen pytest tests/test_server.py -v
```

## Implementation Phases

The project was implemented in 10 phases (see IMPLEMENTATION.md):

1. **Phase 1**: Project Setup - uv, ruff, pytest, pre-commit
2. **Phase 2**: Database Schema & Models - SQLite schema, Quote/Tag models
3. **Phase 3**: Database Operations - CRUD operations, search, tagging
4. **Phase 4**: Seed Data - 20+ Douglas Adams quotes
5. **Phase 5**: MCP Server Core - Server initialization, stdio transport
6. **Phase 6**: MCP Tools - 7 tools for actions
7. **Phase 7**: MCP Resources - 7 resources for read-only access
8. **Phase 8**: MCP Prompts - 3 prompts for LLM guidance
9. **Phase 9**: Development Test Client - CLI for testing without Claude Desktop
10. **Phase 10**: Testing, Documentation & Polish - This phase

## Working with This Codebase

### Adding a New Tool

1. Add tool function in `src/mcp_theanswer/mcp/tools.py`
2. Register tool in `register_tools()` function
3. Add tests in `tests/test_tools.py`
4. Update README.md tool list

### Adding a New Resource

1. Add resource handler in `src/mcp_theanswer/mcp/resources.py`
2. Add resource to `get_resource_list()` function
3. Add URI handling in `read_resource_content()` function
4. Add tests in `tests/test_resources.py`
5. Update README.md resource list

### Adding a New Prompt

1. Add prompt definition to `get_prompt_list()` in `src/mcp_theanswer/mcp/prompts.py`
2. Add prompt handler function (e.g., `_get_my_prompt()`)
3. Add routing in `get_prompt_content()` function
4. Add tests in `tests/test_prompts.py`
5. Update README.md prompt list

### Modifying the Database Schema

1. Update schema in `src/mcp_theanswer/database/schema.py`
2. Increment CURRENT_SCHEMA_VERSION
3. Add migration logic in `migrate_database()` function
4. Update models in `src/mcp_theanswer/database/models.py`
5. Update operations in `src/mcp_theanswer/database/operations.py`
6. Add tests for migration and new functionality
7. Test with existing databases

## Common Development Tasks

### Manual Testing with Claude Desktop

1. Update `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
2. Add server configuration with absolute path to project
3. Restart Claude Desktop
4. Ask Claude: "What tools do you have access to?"
5. Test tools: "Add a quote: 'Test' by 'Author'"
6. Test resources: Ask Claude about quote collections
7. Test prompts: "Find me quotes about life"

### Debugging MCP Communication

- Check server logs: stderr output (logs go to stderr in MCP)
- Use development test client for isolated testing
- Enable DEBUG logging: `QUOTE_VAULT_LOG_LEVEL=DEBUG`
- Check Claude Desktop logs: `~/Library/Logs/Claude/` (macOS)

### Performance Considerations

- SQLite uses WAL mode for better concurrency
- Queries are optimized with indices (quotes.author, tags.name)
- In-memory databases for testing (fast)
- No N+1 queries - tags are fetched efficiently

## References

- Design document: `DESIGN.md`
- Implementation plan: `IMPLEMENTATION.md`
- MCP specification: https://spec.modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Claude Desktop: https://claude.ai/download
