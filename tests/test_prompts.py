"""Tests for MCP prompts."""

import pytest

from mcp_theanswer.mcp.prompts import get_prompt_content, get_prompt_list

# Tests for prompt listing


@pytest.mark.asyncio
async def test_should_list_all_prompts() -> None:
    """Test listing all available prompts."""
    prompts = await get_prompt_list()

    assert len(prompts) == 3

    # Check prompt names
    names = [p.name for p in prompts]
    assert "find-inspiration" in names
    assert "quote-explainer" in names
    assert "add-quote-helper" in names

    # Verify each prompt has required fields
    for prompt in prompts:
        assert prompt.name
        assert prompt.description
        assert prompt.arguments is not None


@pytest.mark.asyncio
async def test_should_have_correct_arguments_for_find_inspiration() -> None:
    """Test find-inspiration prompt has correct arguments."""
    prompts = await get_prompt_list()
    prompt = next(p for p in prompts if p.name == "find-inspiration")

    assert len(prompt.arguments) == 1
    assert prompt.arguments[0].name == "situation"
    assert prompt.arguments[0].required is True


@pytest.mark.asyncio
async def test_should_have_correct_arguments_for_quote_explainer() -> None:
    """Test quote-explainer prompt has correct arguments."""
    prompts = await get_prompt_list()
    prompt = next(p for p in prompts if p.name == "quote-explainer")

    assert len(prompt.arguments) == 2

    # Check quote_text argument
    quote_text_arg = next(a for a in prompt.arguments if a.name == "quote_text")
    assert quote_text_arg.required is True

    # Check author argument
    author_arg = next(a for a in prompt.arguments if a.name == "author")
    assert author_arg.required is False


@pytest.mark.asyncio
async def test_should_have_correct_arguments_for_add_quote_helper() -> None:
    """Test add-quote-helper prompt has correct arguments."""
    prompts = await get_prompt_list()
    prompt = next(p for p in prompts if p.name == "add-quote-helper")

    assert len(prompt.arguments) == 1
    assert prompt.arguments[0].name == "raw_input"
    assert prompt.arguments[0].required is True


# Tests for find-inspiration prompt


@pytest.mark.asyncio
async def test_should_get_find_inspiration_prompt_with_situation() -> None:
    """Test getting find-inspiration prompt with situation argument."""
    result = await get_prompt_content("find-inspiration", {"situation": "feeling lost in life"})

    assert result.description
    assert "feeling lost in life" in result.description
    assert len(result.messages) == 1

    message = result.messages[0]
    assert message.role == "user"
    assert "feeling lost in life" in message.content.text
    assert "Quote Vault" in message.content.text
    assert "search_quotes" in message.content.text
    assert "random_quote" in message.content.text


@pytest.mark.asyncio
async def test_should_reject_find_inspiration_without_situation() -> None:
    """Test that find-inspiration requires situation argument."""
    with pytest.raises(ValueError, match="Missing required argument: situation"):
        await get_prompt_content("find-inspiration", {})


# Tests for quote-explainer prompt


@pytest.mark.asyncio
async def test_should_get_quote_explainer_prompt_with_quote_and_author() -> None:
    """Test getting quote-explainer prompt with quote_text and author."""
    result = await get_prompt_content(
        "quote-explainer",
        {"quote_text": "The answer is 42", "author": "Douglas Adams"},
    )

    assert result.description
    assert "Douglas Adams" in result.description
    assert len(result.messages) == 1

    message = result.messages[0]
    assert message.role == "user"
    assert "The answer is 42" in message.content.text
    assert "Douglas Adams" in message.content.text
    assert "literal meaning" in message.content.text
    assert "philosophical" in message.content.text


@pytest.mark.asyncio
async def test_should_get_quote_explainer_prompt_without_author() -> None:
    """Test getting quote-explainer prompt without optional author."""
    result = await get_prompt_content(
        "quote-explainer",
        {"quote_text": "To be or not to be"},
    )

    assert result.description
    assert len(result.messages) == 1

    message = result.messages[0]
    assert message.role == "user"
    assert "To be or not to be" in message.content.text
    assert "Unknown" in message.content.text  # Default author


@pytest.mark.asyncio
async def test_should_reject_quote_explainer_without_quote_text() -> None:
    """Test that quote-explainer requires quote_text argument."""
    with pytest.raises(ValueError, match="Missing required argument: quote_text"):
        await get_prompt_content("quote-explainer", {"author": "Someone"})


# Tests for add-quote-helper prompt


@pytest.mark.asyncio
async def test_should_get_add_quote_helper_prompt_with_raw_input() -> None:
    """Test getting add-quote-helper prompt with raw_input."""
    result = await get_prompt_content(
        "add-quote-helper",
        {"raw_input": "I heard this great quote about life being like a box of chocolates"},
    )

    assert result.description
    assert "add" in result.description.lower()
    assert len(result.messages) == 1

    message = result.messages[0]
    assert message.role == "user"
    assert "box of chocolates" in message.content.text
    assert "Quote Vault" in message.content.text
    assert "add_quote" in message.content.text
    assert "Extract" in message.content.text


@pytest.mark.asyncio
async def test_should_reject_add_quote_helper_without_raw_input() -> None:
    """Test that add-quote-helper requires raw_input argument."""
    with pytest.raises(ValueError, match="Missing required argument: raw_input"):
        await get_prompt_content("add-quote-helper", {})


# Tests for error handling


@pytest.mark.asyncio
async def test_should_handle_unknown_prompt_name() -> None:
    """Test handling of unknown prompt name."""
    with pytest.raises(ValueError, match="Unknown prompt"):
        await get_prompt_content("nonexistent-prompt", {"some": "arg"})


@pytest.mark.asyncio
async def test_should_handle_empty_arguments_dict() -> None:
    """Test that empty arguments dict is handled correctly."""
    with pytest.raises(ValueError, match="Missing required argument"):
        await get_prompt_content("find-inspiration", {})


# Tests for prompt content structure


@pytest.mark.asyncio
async def test_should_return_correct_message_structure() -> None:
    """Test that all prompts return correct message structure."""
    prompts_to_test = [
        ("find-inspiration", {"situation": "test"}),
        ("quote-explainer", {"quote_text": "test"}),
        ("add-quote-helper", {"raw_input": "test"}),
    ]

    for prompt_name, args in prompts_to_test:
        result = await get_prompt_content(prompt_name, args)

        # Check structure
        assert result.description
        assert isinstance(result.messages, list)
        assert len(result.messages) > 0

        # Check message format
        message = result.messages[0]
        assert message.role == "user"
        assert hasattr(message.content, "text")
        assert hasattr(message.content, "type")
        assert message.content.type == "text"
        assert isinstance(message.content.text, str)
        assert len(message.content.text) > 0
