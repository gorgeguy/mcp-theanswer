# Quote Vault MCP Server - Design Document

## Overview

Quote Vault is an MCP (Model Context Protocol) server that manages a personal collection of quotes. It demonstrates all three MCP primitives: Tools (for actions), Resources (for data access), and Prompts (for LLM guidance). The server stores quotes in a SQLite database and comes pre-seeded with Douglas Adams quotes, including the famous "42" reference.

## Design Decisions

### Storage

- **SQLite database** for persistence
- Database file location: `~/.quote-vault/quotes.db` (or configurable)
- Automatic schema creation on first run
- Migrations support for future schema changes

### Data Model

#### Quote Entity

```python
{
    "id": int,              # Auto-increment primary key
    "text": str,            # The quote text (required)
    "author": str,          # Author name (required)
    "source": str | None,   # Book, speech, etc.
    "year": int | None,     # Year published/said
    "created_at": str,      # ISO 8601 timestamp
    "tags": List[str]       # Associated tags (many-to-many)
}
```

#### Database Schema

```sql
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    author TEXT NOT NULL,
    source TEXT,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE quote_tags (
    quote_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (quote_id, tag_id),
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_quotes_author ON quotes(author);
CREATE INDEX idx_tags_name ON tags(name);
```

## MCP Interface Design

### Tools (Actions/Mutations)

#### 1. `add_quote`

Add a new quote to the vault.

**Input:**

```json
{
  "text": "string (required)",
  "author": "string (required)",
  "source": "string (optional)",
  "year": "integer (optional)",
  "tags": ["string array (optional)"]
}
```

**Output:**

```json
{
  "id": 42,
  "message": "Quote added successfully"
}
```

#### 2. `search_quotes`

Search for quotes using simple substring matching.

**Input:**

```json
{
  "query": "string (optional) - searches text and author",
  "author": "string (optional) - filter by author",
  "tags": ["string array (optional) - filter by tags (AND logic)"]
}
```

**Output:**

```json
{
  "quotes": [
    {
      "id": 1,
      "text": "...",
      "author": "...",
      "source": "...",
      "year": 1979,
      "tags": ["philosophy", "humor"]
    }
  ],
  "count": 1
}
```

#### 3. `random_quote`

Get a random quote, optionally filtered by tag.

**Input:**

```json
{
  "tag": "string (optional)"
}
```

**Output:**

```json
{
  "quote": {
    /* full quote object */
  }
}
```

#### 4. `update_quote`

Update an existing quote.

**Input:**

```json
{
  "id": "integer (required)",
  "text": "string (optional)",
  "author": "string (optional)",
  "source": "string (optional)",
  "year": "integer (optional)",
  "tags": ["string array (optional) - replaces all tags"]
}
```

**Output:**

```json
{
  "success": true,
  "message": "Quote updated successfully"
}
```

#### 5. `delete_quote`

Delete a quote by ID.

**Input:**

```json
{
  "id": "integer (required)"
}
```

**Output:**

```json
{
  "success": true,
  "message": "Quote deleted successfully"
}
```

#### 6. `add_tag_to_quote`

Add a tag to an existing quote.

**Input:**

```json
{
  "quote_id": "integer (required)",
  "tag": "string (required)"
}
```

**Output:**

```json
{
  "success": true,
  "message": "Tag added successfully"
}
```

#### 7. `list_tags`

List all unique tags in the system.

**Input:** None

**Output:**

```json
{
  "tags": [
    { "name": "philosophy", "count": 15 },
    { "name": "humor", "count": 23 }
  ]
}
```

### Resources (Read-only Data Access)

Resources provide URI-based access to quote data. They return content that can be read by LLMs.

#### 1. `quote://all`

Returns all quotes in the vault.

**Format:** JSON array of quote objects

#### 2. `quote://id/{id}`

Returns a specific quote by ID.

**Example:** `quote://id/42`

**Format:** Single quote object as JSON

#### 3. `quote://author/{author}`

Returns all quotes by a specific author.

**Example:** `quote://author/Douglas Adams`

**Format:** JSON array of quote objects

#### 4. `quote://tag/{tag}`

Returns all quotes with a specific tag.

**Example:** `quote://tag/philosophy`

**Format:** JSON array of quote objects

#### 5. `quote://random`

Returns a random quote from the collection.

**Format:** Single quote object as JSON

#### 6. `quote://stats`

Returns statistics about the quote collection.

**Format:**

```json
{
  "total_quotes": 42,
  "total_authors": 15,
  "total_tags": 8,
  "most_quoted_author": "Douglas Adams (12 quotes)",
  "most_common_tag": "philosophy (20 quotes)"
}
```

#### 7. `quote://tags`

Returns all available tags with counts.

**Format:** JSON array of tag objects

### Prompts (LLM Guidance)

Prompts help guide the LLM to use the Quote Vault effectively for specific tasks.

#### 1. `find-inspiration`

Helps users find relevant quotes for their current situation or question.

**Prompt Template:**

```
You are helping a user find inspirational or relevant quotes from their personal Quote Vault.

User's situation or question: {{situation}}

Your task:
1. Understand what the user is looking for
2. Search the quote vault using appropriate keywords and tags
3. Present the most relevant quotes with explanation of why they're relevant
4. If no perfect match, suggest related quotes or offer to help add new ones

Available tools: search_quotes, random_quote
Available resources: quote://tag/*, quote://author/*

Be thoughtful and consider the emotional or philosophical context of their request.
```

**Arguments:**

- `situation` (string, required): The user's current situation or question

#### 2. `quote-explainer`

Helps analyze and explain the deeper meaning of quotes.

**Prompt Template:**

```
You are a literary and philosophical analyst helping users understand quotes more deeply.

Quote to analyze: {{quote_text}}
Author: {{author}}

Your task:
1. Explain the literal meaning
2. Discuss the deeper philosophical or metaphorical meaning
3. Provide historical or cultural context if relevant
4. Suggest how this quote might apply to modern life
5. Identify related themes or concepts

Be insightful but accessible. Use examples to illustrate your points.
```

**Arguments:**

- `quote_text` (string, required): The quote to analyze
- `author` (string, optional): The quote's author

#### 3. `add-quote-helper`

Guides users through adding well-structured quotes.

**Prompt Template:**

```
You are helping a user add a new quote to their Quote Vault.

User wants to add: {{raw_input}}

Your task:
1. Extract the quote text and author from their input
2. Ask clarifying questions if needed (source, year, context)
3. Suggest appropriate tags based on the quote's themes
4. Format everything properly
5. Use the add_quote tool to save it

Be conversational and helpful. Ensure accuracy - verify author attribution if uncertain.
```

**Arguments:**

- `raw_input` (string, required): User's raw input about the quote they want to add

## Implementation Architecture

### Technology Stack

- **Language:** Python 3.11+
- **MCP SDK:** `mcp` Python package
- **Database:** SQLite3 (built-in)
- **Testing:** pytest, pytest-asyncio
- **Type Hints:** Full typing throughout

### Project Structure

```
src/mcp_theanswer/
├── __init__.py
├── main.py                 # Original "42" functionality
├── server.py              # MCP server entry point
├── database/
│   ├── __init__.py
│   ├── schema.py          # Database schema and migrations
│   ├── models.py          # Quote and Tag data models
│   └── operations.py      # CRUD operations
├── mcp/
│   ├── __init__.py
│   ├── tools.py           # MCP tool implementations
│   ├── resources.py       # MCP resource implementations
│   └── prompts.py         # MCP prompt definitions
└── seed_data.py           # Douglas Adams quotes seed data

scripts/
└── test_client.py         # Development MCP test client

tests/
├── test_database.py       # Database operation tests
├── test_tools.py          # MCP tool tests
├── test_resources.py      # MCP resource tests
└── fixtures/              # Test data
```

### Seed Data

The vault will come pre-loaded with 15-20 carefully selected Douglas Adams quotes, including:

- The famous "42" quote
- Philosophy of life quotes
- Humor and wit
- Technology and society
- Various sources (Hitchhiker's Guide series, Dirk Gently, etc.)

Tags will include: `philosophy`, `humor`, `life`, `technology`, `existence`, `satire`

## Search Implementation

### Simple Substring Matching

- Case-insensitive LIKE queries on text and author fields
- Tag filtering using JOIN with AND logic (quote must have ALL specified tags)
- No ranking or relevance scoring in v1
- SQL example:

```sql
SELECT DISTINCT q.* FROM quotes q
LEFT JOIN quote_tags qt ON q.id = qt.quote_id
LEFT JOIN tags t ON qt.tag_id = t.id
WHERE (q.text LIKE '%search%' OR q.author LIKE '%search%')
AND (t.name IN ('tag1', 'tag2') OR :tags_empty)
GROUP BY q.id
HAVING COUNT(DISTINCT t.id) = :tag_count OR :tags_empty
```

## Configuration

### Environment Variables / Config File

```python
{
    "database_path": "~/.quote-vault/quotes.db",  # Database location
    "auto_seed": true,                             # Seed on first run
    "log_level": "INFO"                            # Logging verbosity
}
```

### MCP Server Configuration

The server will be configured in the MCP settings file:

```json
{
  "mcpServers": {
    "quote-vault": {
      "command": "uv",
      "args": ["run", "mcp-theanswer-server"]
    }
  }
}
```

## Development Test Client

A simple MCP client will be included as a development tool to facilitate testing and learning.

### Purpose

- Test the MCP server during development without requiring Claude Desktop
- Understand how MCP clients interact with servers
- Validate tool invocations and resource fetching
- Debug server responses
- Learn the client-side MCP protocol

### Functionality

The test client (`scripts/test_client.py`) will support:

1. **Tool Invocation**
   - Call any tool by name with JSON arguments
   - Display formatted results
   - Example: `python scripts/test_client.py tool add_quote '{"text": "...", "author": "..."}'`

2. **Resource Fetching**
   - Read any resource by URI
   - Display formatted content
   - Example: `python scripts/test_client.py resource quote://random`

3. **Prompt Testing**
   - List available prompts
   - View prompt templates with arguments
   - Example: `python scripts/test_client.py prompt find-inspiration '{"situation": "..."}'`

4. **Interactive Mode**
   - Optional REPL-style interface for exploration
   - Tab completion for commands
   - History support

### Implementation Notes

- Uses the `mcp` Python SDK client libraries
- Connects to the server via stdio transport
- Simple CLI argument parsing (argparse)
- Pretty-printed JSON output
- Error handling and display
- Not intended for production use - development tool only

### Example Usage

```bash
# Add a quote
uv run python scripts/test_client.py tool add_quote \
  '{"text": "The Answer is 42", "author": "Deep Thought", "tags": ["philosophy"]}'

# Search quotes
uv run python scripts/test_client.py tool search_quotes \
  '{"query": "life", "tags": ["philosophy"]}'

# Fetch a resource
uv run python scripts/test_client.py resource quote://stats

# Get random quote
uv run python scripts/test_client.py resource quote://random

# List available tools
uv run python scripts/test_client.py list-tools

# List available resources
uv run python scripts/test_client.py list-resources
```

## Testing Strategy

1. **Unit Tests**
   - Database operations (CRUD)
   - Search logic
   - Data validation

2. **Integration Tests**
   - MCP tool execution
   - Resource fetching
   - Prompt templates

3. **Test Database**
   - Use in-memory SQLite (`:memory:`) for tests
   - Seed with fixture data
   - Clean slate for each test

4. **Manual Testing**
   - Use development test client for exploratory testing
   - Validate against Claude Desktop or other MCP clients
   - Test all tools, resources, and prompts interactively

## Future Enhancements (Out of Scope for v1)

- Import/export functionality (JSON, CSV)
- Backup and restore
- Full-text search with ranking
- Quote collections/playlists
- Sharing quotes (export as image, text)
- API for external integrations
- Web UI for browsing
- Favorite/rating system
- Full-featured end-user CLI (separate from development test client)

## Design Decisions (Resolved)

1. **Error Handling:** Detailed but friendly error messages that aid debugging while remaining user-readable

2. **Quote Validation:**
   - Require non-empty text and author fields
   - No duplicate detection (quotes can legitimately repeat in different contexts)
   - No length limits in v1

3. **Tag Management:** Keep it simple in v1 - no rename/merge functionality, tags persist until manually deleted

4. **Resource Format:** Return formatted text with clear structure for better LLM consumption rather than raw JSON

5. **CLI Tool:** Development test client included for testing and learning; full end-user CLI deferred to future enhancements

## Success Criteria

The Quote Vault MCP server will be considered successful when:

1. All three MCP primitives (Tools, Resources, Prompts) are functional
2. Users can add, search, and retrieve quotes
3. Resources provide useful read-only access patterns
4. Prompts effectively guide LLM behavior for quote-related tasks
5. Comprehensive test coverage (>80%)
6. Clear documentation for setup and usage
