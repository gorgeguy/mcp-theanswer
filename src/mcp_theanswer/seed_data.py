"""Seed data with Douglas Adams quotes."""

from pathlib import Path

from mcp_theanswer.database.operations import add_quote
from mcp_theanswer.database.schema import check_if_seeded

# Collection of Douglas Adams quotes with metadata
SEED_QUOTES = [
    {
        "text": "The answer to the great question of life, the universe and everything is forty-two.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["philosophy", "humor", "existence", "famous"],
    },
    {
        "text": "Don't Panic.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["humor", "life", "wisdom", "famous"],
    },
    {
        "text": "Time is an illusion. Lunchtime doubly so.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["philosophy", "humor", "time", "absurdism"],
    },
    {
        "text": "In the beginning the Universe was created. This has made a lot of people very angry and been widely regarded as a bad move.",
        "author": "Douglas Adams",
        "source": "The Restaurant at the End of the Universe",
        "year": 1980,
        "tags": ["philosophy", "humor", "existence", "satire"],
    },
    {
        "text": "I may not have gone where I intended to go, but I think I have ended up where I needed to be.",
        "author": "Douglas Adams",
        "source": "The Long Dark Tea-Time of the Soul",
        "year": 1988,
        "tags": ["life", "wisdom", "philosophy", "journey"],
    },
    {
        "text": "A learning experience is one of those things that says, 'You know that thing you just did? Don't do that.'",
        "author": "Douglas Adams",
        "source": "The Salmon of Doubt",
        "year": 2002,
        "tags": ["wisdom", "humor", "life", "learning"],
    },
    {
        "text": "I love deadlines. I love the whooshing noise they make as they go by.",
        "author": "Douglas Adams",
        "source": "The Salmon of Doubt",
        "year": 2002,
        "tags": ["humor", "life", "work", "procrastination"],
    },
    {
        "text": "The fact that we live at the bottom of a deep gravity well, on the surface of a gas covered planet going around a nuclear fireball 90 million miles away and think this to be normal is obviously some indication of how skewed our perspective tends to be.",
        "author": "Douglas Adams",
        "source": "The Salmon of Doubt",
        "year": 2002,
        "tags": ["philosophy", "science", "perspective", "existence"],
    },
    {
        "text": "For instance, on the planet Earth, man had always assumed that he was more intelligent than dolphins because he had achieved so much—the wheel, New York, wars and so on—whilst all the dolphins had ever done was muck about in the water having a good time. But conversely, the dolphins had always believed that they were far more intelligent than man—for precisely the same reasons.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["philosophy", "humor", "intelligence", "perspective", "satire"],
    },
    {
        "text": "Let's think the unthinkable, let's do the undoable. Let us prepare to grapple with the ineffable itself, and see if we may not eff it after all.",
        "author": "Douglas Adams",
        "source": "Dirk Gently's Holistic Detective Agency",
        "year": 1987,
        "tags": ["philosophy", "humor", "language", "challenge"],
    },
    {
        "text": "There is a theory which states that if ever anyone discovers exactly what the Universe is for and why it is here, it will instantly disappear and be replaced by something even more bizarre and inexplicable. There is another theory which states that this has already happened.",
        "author": "Douglas Adams",
        "source": "The Restaurant at the End of the Universe",
        "year": 1980,
        "tags": ["philosophy", "humor", "existence", "mystery", "absurdism"],
    },
    {
        "text": "We demand rigidly defined areas of doubt and uncertainty!",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["humor", "philosophy", "certainty", "absurdism"],
    },
    {
        "text": "It is a mistake to think you can solve any major problems just with potatoes.",
        "author": "Douglas Adams",
        "source": "Life, the Universe and Everything",
        "year": 1982,
        "tags": ["humor", "wisdom", "absurdism"],
    },
    {
        "text": "Anyone who is capable of getting themselves made President should on no account be allowed to do the job.",
        "author": "Douglas Adams",
        "source": "The Restaurant at the End of the Universe",
        "year": 1980,
        "tags": ["politics", "humor", "satire", "wisdom"],
    },
    {
        "text": "Nothing travels faster than the speed of light, with the possible exception of bad news, which obeys its own special laws.",
        "author": "Douglas Adams",
        "source": "Mostly Harmless",
        "year": 1992,
        "tags": ["humor", "science", "absurdism"],
    },
    {
        "text": "The ships hung in the sky in much the same way that bricks don't.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["humor", "science-fiction", "imagery", "absurdism"],
    },
    {
        "text": "If there's anything more important than my ego around, I want it caught and shot now.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["humor", "ego", "satire", "character"],
    },
    {
        "text": "Human beings, who are almost unique in having the ability to learn from the experience of others, are also remarkable for their apparent disinclination to do so.",
        "author": "Douglas Adams",
        "source": "Last Chance to See",
        "year": 1990,
        "tags": ["wisdom", "philosophy", "human-nature", "learning"],
    },
    {
        "text": "I'd far rather be happy than right any day.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["wisdom", "life", "happiness", "philosophy"],
    },
    {
        "text": "The mere thought hadn't even begun to speculate about the merest possibility of crossing my mind.",
        "author": "Douglas Adams",
        "source": "The Hitchhiker's Guide to the Galaxy",
        "year": 1979,
        "tags": ["humor", "language", "absurdism"],
    },
]


def seed_database(db_path: Path, *, force: bool = False) -> tuple[int, int]:
    """
    Seed the database with Douglas Adams quotes.

    This function is idempotent - running it multiple times will not create
    duplicate entries unless force=True is specified.

    Args:
        db_path: Path to the database file
        force: If True, seed even if database already contains quotes (default: False)

    Returns:
        tuple[int, int]: (number of quotes added, total quotes in database)

    Raises:
        Exception: If database seeding fails
    """
    # Check if database already has quotes (unless forcing)
    if not force and check_if_seeded(db_path):
        # Database already seeded, skip
        from mcp_theanswer.database.operations import get_all_quotes

        existing_quotes = get_all_quotes(db_path)
        return (0, len(existing_quotes))

    # Add all seed quotes
    added_count = 0
    for quote_data in SEED_QUOTES:
        try:
            add_quote(
                db_path,
                text=quote_data["text"],
                author=quote_data["author"],
                source=quote_data.get("source"),
                year=quote_data.get("year"),
                tags=quote_data.get("tags"),
            )
            added_count += 1
        except Exception as e:
            # Log error but continue with other quotes
            print(f"Warning: Failed to add quote: {quote_data['text'][:50]}... Error: {e}")

    # Get total count
    from mcp_theanswer.database.operations import get_all_quotes

    all_quotes = get_all_quotes(db_path)
    return (added_count, len(all_quotes))
