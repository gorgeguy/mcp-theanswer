# mcp-theanswer

A Python project with modern tooling and best practices.

## Description

This project provides the answer to life, the universe, and everything. Built with modern Python development tools and following best practices.

## Features

- Modern Python 3.11+ codebase
- Type hints throughout
- Comprehensive testing with pytest
- Code formatting and linting with ruff
- Pre-commit hooks for code quality
- Full test coverage reporting

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Make sure you have uv installed first.

### For Users

```bash
# Install the package
uv pip install -e .

# Run the application
mcp-theanswer
```

### For Developers

```bash
# Clone the repository
git clone <repository-url>
cd mcp-theanswer

# Install with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install
```

## Usage

```python
from mcp_theanswer.main import get_answer

# Get the answer
answer = get_answer()
print(f"The answer is: {answer}")
```

Or run from the command line:

```bash
mcp-theanswer
```

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run --frozen pytest

# Run tests in verbose mode
uv run --frozen pytest -v

# Run specific test file
uv run --frozen pytest tests/test_main.py
```

### Code Quality

```bash
# Format code
uv run --frozen ruff format .

# Lint code
uv run --frozen ruff check .

# Fix linting issues automatically
uv run --frozen ruff check . --fix

# Type checking
uv run --frozen pyright
```

### Pre-commit Hooks

Pre-commit hooks run automatically on git commit. To run manually:

```bash
# Run on all files
uv run pre-commit run --all-files

# Run on staged files only
uv run pre-commit run
```

## Project Structure

```
mcp-theanswer/
├── .gitignore                  # Git ignore patterns
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── README.md                   # This file
├── pyproject.toml              # Project configuration and dependencies
├── src/
│   └── mcp_theanswer/          # Main package
│       ├── __init__.py         # Package initialization
│       └── main.py             # Main application logic
└── tests/
    ├── __init__.py
    └── test_main.py            # Tests for main module
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass (`uv run --frozen pytest`)
5. Run code quality checks (`uv run --frozen ruff check . && uv run --frozen ruff format .`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast dependency management
- Code quality with [ruff](https://github.com/astral-sh/ruff)
- Testing with [pytest](https://pytest.org/)
