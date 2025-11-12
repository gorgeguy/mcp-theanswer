"""Database CRUD operations."""

import random
import sqlite3
from pathlib import Path

from mcp_theanswer.database.models import Quote


class QuoteNotFoundError(Exception):
    """Raised when a quote is not found."""

    pass


class InvalidInputError(Exception):
    """Raised when input validation fails."""

    pass


def _get_connection(db_path: Path) -> sqlite3.Connection:
    """
    Get a database connection with foreign keys enabled.

    Args:
        db_path: Path to the database file

    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _get_or_create_tag(conn: sqlite3.Connection, tag_name: str) -> int:
    """
    Get tag ID by name, creating it if it doesn't exist.

    Args:
        conn: Database connection
        tag_name: Name of the tag

    Returns:
        int: Tag ID
    """
    # Try to get existing tag
    cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    # Create new tag
    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
    return cursor.lastrowid


def _get_tags_for_quote(conn: sqlite3.Connection, quote_id: int) -> list[str]:
    """
    Get all tag names for a quote.

    Args:
        conn: Database connection
        quote_id: ID of the quote

    Returns:
        list[str]: List of tag names
    """
    cursor = conn.execute(
        """
        SELECT t.name FROM tags t
        JOIN quote_tags qt ON t.id = qt.tag_id
        WHERE qt.quote_id = ?
        ORDER BY t.name
        """,
        (quote_id,),
    )
    return [row[0] for row in cursor.fetchall()]


def add_quote(
    db_path: Path,
    text: str,
    author: str,
    source: str | None = None,
    year: int | None = None,
    tags: list[str] | None = None,
) -> Quote:
    """
    Add a new quote to the database.

    Args:
        db_path: Path to the database file
        text: Quote text (required, non-empty)
        author: Author name (required, non-empty)
        source: Source of the quote
        year: Year the quote was published/said
        tags: List of tag names

    Returns:
        Quote: The newly created quote

    Raises:
        InvalidInputError: If text or author is empty
    """
    # Validate inputs
    if not text or not text.strip():
        raise InvalidInputError("Quote text cannot be empty")
    if not author or not author.strip():
        raise InvalidInputError("Author name cannot be empty")

    conn = _get_connection(db_path)
    try:
        # Insert quote
        cursor = conn.execute(
            "INSERT INTO quotes (text, author, source, year) VALUES (?, ?, ?, ?)",
            (text.strip(), author.strip(), source, year),
        )
        quote_id = cursor.lastrowid

        # Add tags
        tag_names = []
        if tags:
            for tag_name in tags:
                if tag_name and tag_name.strip():
                    tag_id = _get_or_create_tag(conn, tag_name.strip())
                    conn.execute(
                        "INSERT INTO quote_tags (quote_id, tag_id) VALUES (?, ?)",
                        (quote_id, tag_id),
                    )
                    tag_names.append(tag_name.strip())

        conn.commit()

        # Fetch the created quote
        cursor = conn.execute(
            "SELECT id, text, author, source, year, created_at FROM quotes WHERE id = ?",
            (quote_id,),
        )
        row = cursor.fetchone()

        return Quote.from_row(row, tag_names)
    finally:
        conn.close()


def get_quote_by_id(db_path: Path, quote_id: int) -> Quote | None:
    """
    Get a quote by its ID.

    Args:
        db_path: Path to the database file
        quote_id: ID of the quote

    Returns:
        Quote | None: The quote if found, None otherwise
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT id, text, author, source, year, created_at FROM quotes WHERE id = ?",
            (quote_id,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        tags = _get_tags_for_quote(conn, quote_id)
        return Quote.from_row(row, tags)
    finally:
        conn.close()


def get_all_quotes(db_path: Path) -> list[Quote]:
    """
    Get all quotes in the database.

    Args:
        db_path: Path to the database file

    Returns:
        list[Quote]: List of all quotes
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT id, text, author, source, year, created_at FROM quotes ORDER BY created_at DESC"
        )
        quotes = []
        for row in cursor.fetchall():
            quote_id = row[0]
            tags = _get_tags_for_quote(conn, quote_id)
            quotes.append(Quote.from_row(row, tags))
        return quotes
    finally:
        conn.close()


def get_quotes_by_author(db_path: Path, author: str) -> list[Quote]:
    """
    Get all quotes by a specific author.

    Args:
        db_path: Path to the database file
        author: Author name

    Returns:
        list[Quote]: List of quotes by the author
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT id, text, author, source, year, created_at FROM quotes
            WHERE author = ?
            ORDER BY created_at DESC
            """,
            (author,),
        )
        quotes = []
        for row in cursor.fetchall():
            quote_id = row[0]
            tags = _get_tags_for_quote(conn, quote_id)
            quotes.append(Quote.from_row(row, tags))
        return quotes
    finally:
        conn.close()


def get_quotes_by_tag(db_path: Path, tag: str) -> list[Quote]:
    """
    Get all quotes with a specific tag.

    Args:
        db_path: Path to the database file
        tag: Tag name

    Returns:
        list[Quote]: List of quotes with the tag
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT DISTINCT q.id, q.text, q.author, q.source, q.year, q.created_at
            FROM quotes q
            JOIN quote_tags qt ON q.id = qt.quote_id
            JOIN tags t ON qt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY q.created_at DESC
            """,
            (tag,),
        )
        quotes = []
        for row in cursor.fetchall():
            quote_id = row[0]
            tags = _get_tags_for_quote(conn, quote_id)
            quotes.append(Quote.from_row(row, tags))
        return quotes
    finally:
        conn.close()


def search_quotes(
    db_path: Path,
    query: str | None = None,
    author: str | None = None,
    tags: list[str] | None = None,
) -> list[Quote]:
    """
    Search for quotes with optional filters.

    Args:
        db_path: Path to the database file
        query: Search text (searches in quote text and author, case-insensitive)
        author: Filter by author (exact match, case-insensitive)
        tags: Filter by tags (quote must have ALL specified tags)

    Returns:
        list[Quote]: List of matching quotes
    """
    conn = _get_connection(db_path)
    try:
        # Build query
        sql = """
            SELECT DISTINCT q.id, q.text, q.author, q.source, q.year, q.created_at
            FROM quotes q
        """
        where_clauses = []
        params = []

        # Add tag joins if filtering by tags
        if tags:
            sql += """
                JOIN quote_tags qt ON q.id = qt.quote_id
                JOIN tags t ON qt.tag_id = t.id
            """
            placeholders = ",".join("?" * len(tags))
            where_clauses.append(f"t.name IN ({placeholders})")
            params.extend(tags)

        # Add text search
        if query:
            where_clauses.append("(q.text LIKE ? OR q.author LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term])

        # Add author filter
        if author:
            where_clauses.append("LOWER(q.author) = LOWER(?)")
            params.append(author)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        # Group by to handle tag filtering (must have ALL tags)
        if tags:
            sql += " GROUP BY q.id HAVING COUNT(DISTINCT t.id) = ?"
            params.append(len(tags))

        sql += " ORDER BY q.created_at DESC"

        cursor = conn.execute(sql, params)
        quotes = []
        for row in cursor.fetchall():
            quote_id = row[0]
            quote_tags = _get_tags_for_quote(conn, quote_id)
            quotes.append(Quote.from_row(row, quote_tags))
        return quotes
    finally:
        conn.close()


def get_random_quote(db_path: Path, tag: str | None = None) -> Quote | None:
    """
    Get a random quote, optionally filtered by tag.

    Args:
        db_path: Path to the database file
        tag: Optional tag to filter by

    Returns:
        Quote | None: Random quote if any exist, None otherwise
    """
    conn = _get_connection(db_path)
    try:
        if tag:
            cursor = conn.execute(
                """
                SELECT DISTINCT q.id, q.text, q.author, q.source, q.year, q.created_at
                FROM quotes q
                JOIN quote_tags qt ON q.id = qt.quote_id
                JOIN tags t ON qt.tag_id = t.id
                WHERE t.name = ?
                """,
                (tag,),
            )
        else:
            cursor = conn.execute("SELECT id, text, author, source, year, created_at FROM quotes")

        rows = cursor.fetchall()
        if not rows:
            return None

        row = random.choice(rows)
        quote_id = row[0]
        tags = _get_tags_for_quote(conn, quote_id)
        return Quote.from_row(row, tags)
    finally:
        conn.close()


def update_quote(db_path: Path, quote_id: int, **kwargs) -> bool:
    """
    Update an existing quote.

    Args:
        db_path: Path to the database file
        quote_id: ID of the quote to update
        **kwargs: Fields to update (text, author, source, year, tags)

    Returns:
        bool: True if quote was updated, False if not found

    Raises:
        InvalidInputError: If text or author is empty
    """
    # Validate inputs
    if "text" in kwargs and (not kwargs["text"] or not kwargs["text"].strip()):
        raise InvalidInputError("Quote text cannot be empty")
    if "author" in kwargs and (not kwargs["author"] or not kwargs["author"].strip()):
        raise InvalidInputError("Author name cannot be empty")

    conn = _get_connection(db_path)
    try:
        # Check if quote exists
        cursor = conn.execute("SELECT id FROM quotes WHERE id = ?", (quote_id,))
        if not cursor.fetchone():
            return False

        # Update quote fields
        update_fields = []
        params = []
        for field in ["text", "author", "source", "year"]:
            if field in kwargs:
                update_fields.append(f"{field} = ?")
                value = kwargs[field]
                if field in ["text", "author"] and value:
                    value = value.strip()
                params.append(value)

        if update_fields:
            sql = f"UPDATE quotes SET {', '.join(update_fields)} WHERE id = ?"
            params.append(quote_id)
            conn.execute(sql, params)

        # Update tags if provided
        if "tags" in kwargs:
            # Remove existing tags
            conn.execute("DELETE FROM quote_tags WHERE quote_id = ?", (quote_id,))

            # Add new tags
            if kwargs["tags"]:
                for tag_name in kwargs["tags"]:
                    if tag_name and tag_name.strip():
                        tag_id = _get_or_create_tag(conn, tag_name.strip())
                        conn.execute(
                            "INSERT INTO quote_tags (quote_id, tag_id) VALUES (?, ?)",
                            (quote_id, tag_id),
                        )

        conn.commit()
        return True
    finally:
        conn.close()


def delete_quote(db_path: Path, quote_id: int) -> bool:
    """
    Delete a quote by ID.

    Args:
        db_path: Path to the database file
        quote_id: ID of the quote to delete

    Returns:
        bool: True if quote was deleted, False if not found
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def add_tag_to_quote(db_path: Path, quote_id: int, tag: str) -> bool:
    """
    Add a tag to an existing quote.

    Args:
        db_path: Path to the database file
        quote_id: ID of the quote
        tag: Tag name to add

    Returns:
        bool: True if tag was added, False if quote not found

    Raises:
        InvalidInputError: If tag is empty
    """
    if not tag or not tag.strip():
        raise InvalidInputError("Tag name cannot be empty")

    conn = _get_connection(db_path)
    try:
        # Check if quote exists
        cursor = conn.execute("SELECT id FROM quotes WHERE id = ?", (quote_id,))
        if not cursor.fetchone():
            return False

        # Get or create tag
        tag_id = _get_or_create_tag(conn, tag.strip())

        # Check if association already exists
        cursor = conn.execute(
            "SELECT 1 FROM quote_tags WHERE quote_id = ? AND tag_id = ?",
            (quote_id, tag_id),
        )
        if cursor.fetchone():
            # Tag already associated with quote
            conn.commit()
            return True

        # Add tag to quote
        conn.execute(
            "INSERT INTO quote_tags (quote_id, tag_id) VALUES (?, ?)",
            (quote_id, tag_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def list_all_tags(db_path: Path) -> list[tuple[str, int]]:
    """
    List all tags with their usage counts.

    Args:
        db_path: Path to the database file

    Returns:
        list[tuple[str, int]]: List of (tag_name, count) tuples, ordered by name
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT t.name, COUNT(qt.quote_id) as count
            FROM tags t
            LEFT JOIN quote_tags qt ON t.id = qt.tag_id
            GROUP BY t.id, t.name
            ORDER BY t.name
            """
        )
        return [(row[0], row[1]) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_statistics(db_path: Path) -> dict:
    """
    Get statistics about the quote collection.

    Args:
        db_path: Path to the database file

    Returns:
        dict: Statistics including counts and top items
    """
    conn = _get_connection(db_path)
    try:
        stats = {}

        # Total quotes
        cursor = conn.execute("SELECT COUNT(*) FROM quotes")
        stats["total_quotes"] = cursor.fetchone()[0]

        # Total authors
        cursor = conn.execute("SELECT COUNT(DISTINCT author) FROM quotes")
        stats["total_authors"] = cursor.fetchone()[0]

        # Total tags
        cursor = conn.execute("SELECT COUNT(*) FROM tags")
        stats["total_tags"] = cursor.fetchone()[0]

        # Most quoted author
        cursor = conn.execute(
            """
            SELECT author, COUNT(*) as count FROM quotes
            GROUP BY author
            ORDER BY count DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row:
            stats["most_quoted_author"] = f"{row[0]} ({row[1]} quotes)"
        else:
            stats["most_quoted_author"] = "N/A"

        # Most common tag
        cursor = conn.execute(
            """
            SELECT t.name, COUNT(qt.quote_id) as count
            FROM tags t
            JOIN quote_tags qt ON t.id = qt.tag_id
            GROUP BY t.id, t.name
            ORDER BY count DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row:
            stats["most_common_tag"] = f"{row[0]} ({row[1]} quotes)"
        else:
            stats["most_common_tag"] = "N/A"

        return stats
    finally:
        conn.close()
