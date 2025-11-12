# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mcp-theanswer is a simple Python application demonstrating modern Python development practices with uv, ruff, pytest, and pre-commit hooks. The project provides a CLI tool that returns "the answer to life, the universe, and everything" (42).

## Development Commands

### Testing

```bash
# Run all tests with coverage (default includes -v, coverage reporting)
uv run --frozen pytest

# Run specific test file
uv run --frozen pytest tests/test_main.py

# Run single test function
uv run --frozen pytest tests/test_main.py::test_should_return_42_when_get_answer_called
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

### Running the Application

```bash
# Run as CLI tool
mcp-theanswer

# Or via Python module
python -m mcp_theanswer.main
```

## Project Structure

- `src/mcp_theanswer/` - Main package source code
  - `main.py` - Contains `get_answer()` and `main()` CLI entry point
- `tests/` - Test files mirroring src structure
  - Test files use descriptive names: `test_should_<expected>_when_<condition>`

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

### Pre-commit Hooks (.pre-commit-config.yaml)

- Ruff formatting and linting with auto-fix
- Prettier for YAML, JSON, and Markdown
- Standard hooks: trailing whitespace, EOF fixer, YAML/JSON/TOML validation, merge conflict detection, debug statement detection

## Architecture Notes

This is a simple single-module application with:

- Core logic in `get_answer()` function (src/mcp_theanswer/main.py:6)
- CLI entry point in `main()` function (src/mcp_theanswer/main.py:16)
- Command-line script configured via pyproject.toml entry point: `mcp-theanswer`

The project uses src-layout (source code in `src/` directory) to ensure proper package installation and avoid import issues during testing.
