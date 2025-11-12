"""Data models for quotes and tags."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Quote:
    """
    Represents a quote in the vault.

    Attributes:
        id: Unique identifier (auto-increment)
        text: The quote text
        author: Author of the quote
        source: Source of the quote (book, speech, etc.)
        year: Year the quote was published/said
        created_at: ISO 8601 timestamp of when quote was added
        tags: List of tags associated with this quote
    """

    id: int
    text: str
    author: str
    source: str | None = None
    year: int | None = None
    created_at: str = ""
    tags: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert quote to dictionary for serialization.

        Returns:
            dict: Quote data as dictionary
        """
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author,
            "source": self.source,
            "year": self.year,
            "created_at": self.created_at,
            "tags": self.tags or [],
        }

    @classmethod
    def from_row(cls, row: tuple[Any, ...], tags: list[str] | None = None) -> "Quote":
        """
        Create a Quote from a database row.

        Args:
            row: Database row tuple (id, text, author, source, year, created_at)
            tags: Optional list of tag names for this quote

        Returns:
            Quote: Quote instance
        """
        return cls(
            id=row[0],
            text=row[1],
            author=row[2],
            source=row[3],
            year=row[4],
            created_at=row[5] if row[5] else datetime.now().isoformat(),
            tags=tags or [],
        )


@dataclass
class Tag:
    """
    Represents a tag in the system.

    Attributes:
        id: Unique identifier (auto-increment)
        name: Tag name
        count: Number of quotes with this tag (when fetching stats)
    """

    id: int
    name: str
    count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert tag to dictionary for serialization.

        Returns:
            dict: Tag data as dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "count": self.count,
        }

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Tag":
        """
        Create a Tag from a database row.

        Args:
            row: Database row tuple (id, name) or (id, name, count)

        Returns:
            Tag: Tag instance
        """
        tag_id = row[0]
        name = row[1]
        count = row[2] if len(row) > 2 else 0
        return cls(id=tag_id, name=name, count=count)
