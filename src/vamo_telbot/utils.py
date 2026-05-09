"""Utility functions for the Telegram bot."""

import re

YOUTUBE_PATTERNS = [
    re.compile(r"(youtu\.be/)"),
    re.compile(r"(youtube\.com/watch\?v=)"),
    re.compile(r"(youtube\.com/shorts/)"),
]


def is_youtube_url(url: str) -> bool:
    """Check if the given URL is a YouTube link.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a YouTube link, False otherwise.
    """
    return any(pattern.search(url) for pattern in YOUTUBE_PATTERNS)
