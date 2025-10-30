"""Main entry point for mcp-theanswer application."""

import sys


def get_answer() -> int:
    """
    Get the answer to life, the universe, and everything.

    Returns:
        int: The answer (42)
    """
    return 42


def main(args: list[str] | None = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        int: Exit code (0 for success)
    """
    if args is None:
        args = sys.argv[1:]

    answer = get_answer()
    print(f"The answer is: {answer}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
