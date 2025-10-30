"""Tests for main module."""

from mcp_theanswer.main import get_answer, main


def test_should_return_42_when_get_answer_called() -> None:
    """Test that get_answer returns 42."""
    assert get_answer() == 42


def test_should_return_zero_when_main_executed_successfully(capsys) -> None:
    """Test that main returns 0 and prints the answer."""
    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "The answer is: 42" in captured.out
