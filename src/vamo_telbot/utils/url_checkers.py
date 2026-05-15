"""URL Checkers module."""

import re

# region URL Patterns
YOUTUBE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(youtu\.be/)", re.IGNORECASE),
    re.compile(r"(youtube\.com/watch\?v=)", re.IGNORECASE),
    re.compile(r"(youtube\.com/shorts/)", re.IGNORECASE),
]
ADULT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"pornhub\.com", re.IGNORECASE),
    re.compile(r"xvideos\.com", re.IGNORECASE),
    re.compile(r"xnxx\.com", re.IGNORECASE),
    re.compile(r"xhamster\.com", re.IGNORECASE),
    re.compile(r"spankbang\.com", re.IGNORECASE),
    re.compile(r"eporner\.com", re.IGNORECASE),
    re.compile(r"youporn\.com", re.IGNORECASE),
    re.compile(r"redtube\.com", re.IGNORECASE),
    re.compile(r"rule34video\.com", re.IGNORECASE),
]
SOCIAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"tiktok\.com", re.IGNORECASE),
    re.compile(r"instagram\.com", re.IGNORECASE),
    re.compile(r"twitter\.com", re.IGNORECASE),
    re.compile(r"x\.com", re.IGNORECASE),  # for the re-branded Twitter
    re.compile(r"facebook\.com", re.IGNORECASE),
]
# endregion URL Patterns


# region URL Checkers
def is_youtube_url(url: str) -> bool:
    """Check if the given URL is a YouTube link.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a YouTube link, False otherwise.
    """
    return any(pattern.search(url) for pattern in YOUTUBE_PATTERNS)


def is_adult_url(url: str) -> bool:
    """Check if the given URL belongs to a known adult website.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL belongs to a known adult website, False otherwise.
    """
    return any(pattern.search(url) for pattern in ADULT_PATTERNS)


def is_social_url(url: str) -> bool:
    """Check if the given URL belongs to a known social media website.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL belongs to a known social media website, False otherwise.
    """
    return any(pattern.search(url) for pattern in SOCIAL_PATTERNS)


# endregion URL Checkers
