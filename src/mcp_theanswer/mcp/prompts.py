"""MCP prompt implementations for Quote Vault."""

import logging

from mcp.server import Server
from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

logger = logging.getLogger("quote-vault")


async def get_prompt_list() -> list[Prompt]:
    """
    Get list of all available prompts.

    Returns:
        list[Prompt]: List of prompt descriptors
    """
    return [
        Prompt(
            name="find-inspiration",
            description="Find relevant quotes for your current situation or question",
            arguments=[
                PromptArgument(
                    name="situation",
                    description="Your current situation or question",
                    required=True,
                )
            ],
        ),
        Prompt(
            name="quote-explainer",
            description="Analyze and explain the deeper meaning of a quote",
            arguments=[
                PromptArgument(
                    name="quote_text",
                    description="The quote to analyze",
                    required=True,
                ),
                PromptArgument(
                    name="author",
                    description="The quote's author (optional)",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="add-quote-helper",
            description="Guide you through adding a well-structured quote",
            arguments=[
                PromptArgument(
                    name="raw_input",
                    description="Your raw input about the quote you want to add",
                    required=True,
                )
            ],
        ),
    ]


async def get_prompt_content(name: str, arguments: dict[str, str]) -> GetPromptResult:
    """
    Get prompt content by name with arguments.

    Args:
        name: Prompt name
        arguments: Prompt arguments

    Returns:
        GetPromptResult: Prompt result with messages

    Raises:
        ValueError: If prompt name is unknown or required arguments are missing
    """
    logger.info(f"Prompt requested: {name} with arguments: {arguments}")

    if name == "find-inspiration":
        return await _get_find_inspiration_prompt(arguments)
    elif name == "quote-explainer":
        return await _get_quote_explainer_prompt(arguments)
    elif name == "add-quote-helper":
        return await _get_add_quote_helper_prompt(arguments)
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def _get_find_inspiration_prompt(arguments: dict[str, str]) -> GetPromptResult:
    """
    Get the find-inspiration prompt content.

    Args:
        arguments: Must contain 'situation' key

    Returns:
        GetPromptResult: Prompt with guidance for finding relevant quotes

    Raises:
        ValueError: If 'situation' argument is missing
    """
    if "situation" not in arguments:
        raise ValueError("Missing required argument: situation")

    situation = arguments["situation"]

    prompt_text = f"""You are helping a user find inspirational or relevant quotes from their personal Quote Vault.

User's situation or question: {situation}

Your task:
1. Understand what the user is looking for
2. Search the quote vault using appropriate keywords and tags
3. Present the most relevant quotes with explanation of why they're relevant
4. If no perfect match, suggest related quotes or offer to help add new ones

Available tools: search_quotes, random_quote
Available resources: quote://tag/*, quote://author/*

Be thoughtful and consider the emotional or philosophical context of their request."""

    return GetPromptResult(
        description=f"Finding inspiration for: {situation}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_text),
            )
        ],
    )


async def _get_quote_explainer_prompt(arguments: dict[str, str]) -> GetPromptResult:
    """
    Get the quote-explainer prompt content.

    Args:
        arguments: Must contain 'quote_text', optionally 'author'

    Returns:
        GetPromptResult: Prompt with guidance for analyzing quotes

    Raises:
        ValueError: If 'quote_text' argument is missing
    """
    if "quote_text" not in arguments:
        raise ValueError("Missing required argument: quote_text")

    quote_text = arguments["quote_text"]
    author = arguments.get("author", "Unknown")

    prompt_text = f"""You are a literary and philosophical analyst helping users understand quotes more deeply.

Quote to analyze: {quote_text}
Author: {author}

Your task:
1. Explain the literal meaning
2. Discuss the deeper philosophical or metaphorical meaning
3. Provide historical or cultural context if relevant
4. Suggest how this quote might apply to modern life
5. Identify related themes or concepts

Be insightful but accessible. Use examples to illustrate your points."""

    return GetPromptResult(
        description=f"Analyzing quote by {author}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_text),
            )
        ],
    )


async def _get_add_quote_helper_prompt(arguments: dict[str, str]) -> GetPromptResult:
    """
    Get the add-quote-helper prompt content.

    Args:
        arguments: Must contain 'raw_input' key

    Returns:
        GetPromptResult: Prompt with guidance for adding quotes

    Raises:
        ValueError: If 'raw_input' argument is missing
    """
    if "raw_input" not in arguments:
        raise ValueError("Missing required argument: raw_input")

    raw_input = arguments["raw_input"]

    prompt_text = f"""You are helping a user add a new quote to their Quote Vault.

User wants to add: {raw_input}

Your task:
1. Extract the quote text and author from their input
2. Ask clarifying questions if needed (source, year, context)
3. Suggest appropriate tags based on the quote's themes
4. Format everything properly
5. Use the add_quote tool to save it

Be conversational and helpful. Ensure accuracy - verify author attribution if uncertain."""

    return GetPromptResult(
        description="Helping add a new quote",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_text),
            )
        ],
    )


def register_prompts(server: Server) -> None:
    """
    Register all MCP prompts with the server.

    Args:
        server: MCP server instance
    """

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List all available prompts."""
        return await get_prompt_list()

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
        """Get a prompt by name with arguments."""
        return await get_prompt_content(name, arguments or {})
