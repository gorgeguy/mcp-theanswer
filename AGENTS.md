# Repository Guidelines

## Project Structure & Modules
- App code lives in `src/mcp_theanswer/`: `server.py` (MCP entry), `config.py`, `seed_data.py`, plus `database/` (schema, models, operations) and `mcp/` (tools, resources, prompts).
- Tests mirror modules under `tests/`; coverage HTML lands in `htmlcov/`.
- Dev helpers in `scripts/` (`scripts/test_client.py` CLI client). Docs in `README.md`, `DESIGN.md`, `IMPLEMENTATION.md`, and `CLAUDE.md`.

## Build, Test, and Development Commands
- Install deps: `uv sync` (use `--frozen` for reproducible installs).
- Run the MCP server: `uv run --frozen python -m mcp_theanswer.server` (set `QUOTE_VAULT_AUTO_SEED=true` to preload Douglas Adams quotes).
- Quick smoke via client: `uv run --frozen python scripts/test_client.py list-tools` or `list-resources`.
- Tests with coverage: `uv run --frozen pytest` (`htmlcov/index.html` for report); add `-k <pattern>` for focused runs.
- Lint/format: `uv run --frozen ruff format .` then `uv run --frozen ruff check .`.
- Type check: `uv run --frozen pyright`. Full sweep: `uv run pre-commit run --all-files`.

## Coding Style & Naming
- Python 3.11+, 4-space indentation, target line length 100; Ruff formats with double quotes.
- Favor type hints and async patterns already used in the server. Avoid print debugging; prefer logging.
- Naming: modules/functions `snake_case`, classes `CapWords`, constants `ALL_CAPS`. Tests: `test_<feature>_<behavior>`.

## Testing Guidelines
- Use `pytest` config in `pyproject.toml`; keep new tests beside related modules in `tests/`.
- Cover DB and MCP behaviors deterministically (seed/fixtures over randomness). Update seed data carefully when assertions depend on it.
- Regenerate coverage when touching core paths: `uv run --frozen pytest --cov-report=html`, then skim `htmlcov/index.html` for gaps.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat:`, `fix:`, `chore:`, etc.) and keep commits scoped with tests.
- PRs should explain intent, list key changes, note testing done, and link issues/tasks. Include CLI output or screenshots when behavior shifts.
- Ensure CI-ready state before review: `uv run --frozen ruff check . && uv run --frozen pyright && uv run --frozen pytest`.
- Mention env vars touched (`QUOTE_VAULT_DB_PATH`, `QUOTE_VAULT_AUTO_SEED`, `QUOTE_VAULT_LOG_LEVEL`) in descriptions when relevant.

## Security & Configuration Notes
- Do not commit local DB files or secrets. Default DB path is user-local; override via env only when necessary.
- Keep dependencies managed by `uv.lock`; prefer `uv lock --upgrade` for bumps and rerun QA commands afterward.

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs via Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push`/`bd dolt pull` for remote sync
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-- END BEADS INTEGRATION -->
