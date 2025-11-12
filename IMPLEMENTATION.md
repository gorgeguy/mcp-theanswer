# Implementation Plan - Quote Vault MCP Server

This document outlines the phased implementation approach for building the Quote Vault MCP server.

## Overview

The implementation is broken into 10 phases, each building on the previous. Each phase includes its own testing to ensure stability before moving forward.

## Phase 1: Project Setup & Dependencies

**Goal:** Set up the project structure and install necessary dependencies.

### Tasks

1. **Add MCP dependencies**

   ```bash
   uv add mcp
   uv add --dev pytest-asyncio
   ```

2. **Create directory structure**

   ```
   src/mcp_theanswer/
   ├── database/
   │   ├── __init__.py
   │   ├── schema.py
   │   ├── models.py
   │   └── operations.py
   ├── mcp/
   │   ├── __init__.py
   │   ├── tools.py
   │   ├── resources.py
   │   └── prompts.py
   ├── server.py
   └── seed_data.py

   scripts/
   └── test_client.py

   tests/
   ├── fixtures/
   │   └── test_quotes.py
   ├── test_database.py
   ├── test_tools.py
   └── test_resources.py
   ```

3. **Update pyproject.toml**
   - Add MCP server entry point: `mcp-theanswer-server`
   - Add any additional dependencies

### Validation

- Directory structure exists
- Dependencies installed
- `uv run --frozen pytest` passes (existing tests still work)

## Phase 2: Database Schema & Models

**Goal:** Implement the SQLite database schema and data models.

### Tasks

1. **Create schema.py**
   - Define SQL schema for quotes, tags, quote_tags tables
   - Create indices
   - Implement `init_database()` function to create tables
   - Implement `check_if_seeded()` function to check for initial data
   - Add migration support structure (for future use)

2. **Create models.py**
   - Define `Quote` dataclass with all fields
   - Define `Tag` dataclass
   - Add type hints throughout
   - Implement `to_dict()` methods for serialization
   - Implement `from_row()` classmethods for database rows

3. **Configuration handling**
   - Create config.py for database path, auto_seed flag
   - Support environment variables and defaults
   - Use pathlib.Path for file paths
   - Default database location: `~/.quote-vault/quotes.db`

### Validation

- Unit tests for model serialization/deserialization
- Schema creation works without errors
- Database file created in correct location
- Tables and indices exist as expected

## Phase 3: Database Operations (CRUD)

**Goal:** Implement all database operations needed by the MCP tools.

### Tasks

1. **Create operations.py**
   - `add_quote(text, author, source, year, tags) -> Quote`
   - `get_quote_by_id(id) -> Quote | None`
   - `get_all_quotes() -> list[Quote]`
   - `search_quotes(query, author, tags) -> list[Quote]`
   - `update_quote(id, **kwargs) -> bool`
   - `delete_quote(id) -> bool`
   - `get_random_quote(tag) -> Quote | None`
   - `add_tag_to_quote(quote_id, tag) -> bool`
   - `list_all_tags() -> list[tuple[str, int]]`
   - `get_quotes_by_author(author) -> list[Quote]`
   - `get_quotes_by_tag(tag) -> list[Quote]`
   - `get_statistics() -> dict`

2. **Error handling**
   - Validate inputs (non-empty text/author)
   - Handle database errors gracefully
   - Return meaningful error messages
   - Use proper exception types

3. **Transaction management**
   - Use context managers for database connections
   - Ensure proper commit/rollback
   - Handle concurrent access safely

### Validation

- Comprehensive unit tests for all CRUD operations
- Test edge cases (empty results, invalid IDs, etc.)
- Test search with various combinations
- Test tag operations
- Use `:memory:` database for tests
- Achieve >90% code coverage for database module

## Phase 4: Seed Data

**Goal:** Create initial Douglas Adams quotes for seeding the database.

### Tasks

1. **Create seed_data.py**
   - Curate 15-20 Douglas Adams quotes
   - Include the famous "42" quote
   - Add variety: philosophy, humor, technology, life
   - Include metadata: source, year, tags
   - Implement `seed_database(db_path)` function
   - Check if already seeded before adding

2. **Quote selection**
   - Quote from Hitchhiker's Guide to the Galaxy
   - Quotes from other books (Restaurant at End of Universe, Life Universe Everything, etc.)
   - Ensure variety in themes
   - Add appropriate tags: philosophy, humor, life, technology, existence, satire

3. **Seeding logic**
   - Only seed if database is empty or explicitly requested
   - Log what was seeded
   - Handle errors gracefully

### Validation

- Manual verification of quote accuracy and attribution
- Test seeding on fresh database
- Test idempotency (seeding twice doesn't duplicate)
- Verify all quotes have proper metadata

## Phase 5: MCP Server Core Setup

**Goal:** Set up the basic MCP server structure and initialization.

### Tasks

1. **Create server.py**
   - Import and initialize MCP server
   - Set up database connection
   - Initialize database schema if needed
   - Seed database if configured
   - Set up logging
   - Register all tools, resources, prompts (placeholders for now)
   - Implement main server entry point

2. **Server lifecycle**
   - Initialize on startup
   - Clean shutdown handling
   - Database connection management
   - Configuration loading

3. **Entry point**
   - Update pyproject.toml with server script
   - Test server starts without errors
   - Verify it responds to basic MCP protocol messages

### Validation

- Server starts without errors
- Database initializes on first run
- Configuration loads correctly
- Can connect via stdio transport
- Logging works as expected

## Phase 6: Implement MCP Tools

**Goal:** Implement all 7 MCP tools for quote management.

### Tasks

1. **Create tools.py with tool implementations**
   - `add_quote` - Add new quote with validation
   - `search_quotes` - Search with filters
   - `random_quote` - Get random quote (optional tag filter)
   - `update_quote` - Update existing quote
   - `delete_quote` - Delete by ID
   - `add_tag_to_quote` - Add tag to existing quote
   - `list_tags` - List all tags with counts

2. **Tool registration**
   - Register each tool with MCP server
   - Define input schemas with proper types
   - Define output schemas
   - Add descriptions for each tool

3. **Input validation**
   - Validate required fields
   - Type checking
   - Return clear error messages for invalid inputs

4. **Output formatting**
   - Consistent response format
   - Include success/error status
   - Include relevant data in responses

### Validation

- Unit tests for each tool
- Test with valid inputs
- Test with invalid inputs
- Test error conditions
- Integration tests with actual database
- Manual testing via development client (once available)

## Phase 7: Implement MCP Resources

**Goal:** Implement all 7 MCP resources for read-only data access.

### Tasks

1. **Create resources.py with resource handlers**
   - `quote://all` - All quotes
   - `quote://id/{id}` - Specific quote by ID
   - `quote://author/{author}` - Quotes by author
   - `quote://tag/{tag}` - Quotes by tag
   - `quote://random` - Random quote
   - `quote://stats` - Statistics
   - `quote://tags` - All tags

2. **URI parsing**
   - Parse resource URIs correctly
   - Extract parameters (id, author, tag)
   - Handle URL encoding (spaces in author names)

3. **Resource registration**
   - Register resource handlers with MCP server
   - Define resource templates
   - Add descriptions

4. **Output formatting**
   - Format as structured text for LLM consumption
   - Include relevant metadata
   - Make output readable and useful

### Validation

- Unit tests for each resource
- Test URI parsing with various inputs
- Test with valid and invalid parameters
- Test output formatting
- Manual testing via development client

## Phase 8: Implement MCP Prompts

**Goal:** Implement all 3 MCP prompts for LLM guidance.

### Tasks

1. **Create prompts.py with prompt definitions**
   - `find-inspiration` - Help find relevant quotes
   - `quote-explainer` - Analyze quote meanings
   - `add-quote-helper` - Guide quote addition

2. **Prompt templates**
   - Write clear, effective prompt text
   - Define required and optional arguments
   - Include instructions for using tools and resources
   - Make prompts conversational and helpful

3. **Prompt registration**
   - Register each prompt with MCP server
   - Define argument schemas
   - Add descriptions

### Validation

- Review prompts for clarity and effectiveness
- Test argument substitution
- Manual testing with Claude Desktop (if available)
- Verify prompts guide LLM behavior as intended

## Phase 9: Development Test Client

**Goal:** Build a simple CLI client for testing the MCP server.

### Tasks

1. **Create scripts/test_client.py**
   - Command-line argument parsing (argparse)
   - Connect to server via stdio transport
   - Support commands:
     - `list-tools` - List available tools
     - `list-resources` - List available resources
     - `list-prompts` - List available prompts
     - `tool <name> <json_args>` - Call a tool
     - `resource <uri>` - Fetch a resource
     - `prompt <name> <json_args>` - Test a prompt
   - Pretty-print JSON output
   - Error handling and display

2. **Optional: Interactive mode**
   - REPL-style interface
   - Command history
   - Tab completion (if time permits)

3. **Documentation**
   - Add usage examples to README
   - Document all commands
   - Include troubleshooting tips

### Validation

- Test all commands work correctly
- Verify connection to server
- Test error handling
- Manual testing of all tools and resources
- Document any issues discovered

## Phase 10: Testing, Documentation & Polish

**Goal:** Comprehensive testing, documentation updates, and final polish.

### Tasks

1. **Test coverage**
   - Ensure >80% overall coverage
   - Add any missing unit tests
   - Add integration tests
   - Test error paths

2. **Documentation**
   - Update README.md with:
     - Installation instructions
     - MCP server setup for Claude Desktop
     - Usage examples
     - Development test client usage
   - Update CLAUDE.md with implementation details
   - Add inline code documentation
   - Add docstrings to all public functions

3. **Manual testing**
   - Test with development client
   - Test with Claude Desktop (if available)
   - Try all tools, resources, prompts
   - Test edge cases
   - Verify seed data is correct

4. **Code quality**
   - Run ruff format and fix any issues
   - Run ruff check and fix any issues
   - Run pyright and fix type errors
   - Run pre-commit hooks

5. **Performance & reliability**
   - Test with larger databases (if needed)
   - Verify database locks work correctly
   - Check for resource leaks
   - Ensure graceful error handling

### Validation

- All tests pass
- Test coverage >80%
- No linting errors
- No type errors
- Documentation is complete and accurate
- Server works with Claude Desktop
- Development client works for all operations

## Implementation Order & Dependencies

```
Phase 1: Project Setup
    ↓
Phase 2: Database Schema & Models
    ↓
Phase 3: Database Operations
    ↓
Phase 4: Seed Data
    ↓
Phase 5: MCP Server Core ← (uses Phases 2-4)
    ↓
Phase 6: MCP Tools ← (uses Phases 3-5)
    ↓
Phase 7: MCP Resources ← (uses Phases 3-5)
    ↓
Phase 8: MCP Prompts ← (uses Phase 5)
    ↓
Phase 9: Test Client ← (uses Phases 5-8)
    ↓
Phase 10: Testing & Polish ← (uses all phases)
```

## Testing Strategy Throughout

- **Unit tests first**: Write tests before or alongside implementation
- **Test each phase**: Don't move to next phase until current phase is tested
- **Integration tests**: Test component interactions
- **Manual testing**: Use development client to verify behavior
- **Continuous validation**: Run tests frequently during development

## Risk Mitigation

1. **MCP SDK Learning Curve**
   - Risk: Unfamiliar with MCP SDK
   - Mitigation: Start with simple examples, read SDK documentation, implement incrementally

2. **Database Concurrency**
   - Risk: SQLite locking issues
   - Mitigation: Use proper transaction management, test concurrent access

3. **Resource URI Parsing**
   - Risk: Complex URI patterns might be tricky
   - Mitigation: Start with simple cases, add complexity incrementally

4. **Prompt Effectiveness**
   - Risk: Prompts might not guide LLM well
   - Mitigation: Iterate on prompts based on testing, get feedback

## Success Metrics

- [ ] All 7 tools working correctly
- [ ] All 7 resources returning proper data
- [ ] All 3 prompts defined and functional
- [ ] Database operations tested and reliable
- [ ] Seed data includes 15-20 Douglas Adams quotes
- [ ] Development test client works for all operations
- [ ] Test coverage >80%
- [ ] No linting or type errors
- [ ] Server works with Claude Desktop
- [ ] Documentation complete

## Estimated Effort

- **Phase 1**: 30 minutes
- **Phase 2**: 1-2 hours
- **Phase 3**: 2-3 hours
- **Phase 4**: 1 hour
- **Phase 5**: 1-2 hours
- **Phase 6**: 2-3 hours
- **Phase 7**: 2-3 hours
- **Phase 8**: 1 hour
- **Phase 9**: 2-3 hours
- **Phase 10**: 2-3 hours

**Total estimated effort**: 14-21 hours (spread across multiple sessions)

## Next Steps

1. Review this implementation plan
2. Get user approval to proceed
3. Start with Phase 1: Project Setup
4. Work through each phase sequentially
5. Test thoroughly at each phase
6. Iterate based on findings
