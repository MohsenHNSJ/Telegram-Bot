"""Tests for utility functions."""

# ruff: noqa: S101, FBT001
import pytest

from vamo_telbot.utils import is_adult_url, is_social_url, is_youtube_url, make_bar


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://youtu.be/dQw4w9WgXcQ", True),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://youtube.com/shorts/dQw4w9WgXcQ", True),
        ("https://vimeo.com/123456", False),
        ("https://example.com/watch?v=dQw4w9WgXcQ", False),
        ("random string", False),
    ],
)
def test_is_youtube_url(url: str, expected: bool) -> None:
    """Test the is_youtube_url function."""
    assert is_youtube_url(url) == expected


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.pornhub.com/view_video.php?viewkey=abc", True),
        ("https://xvideos.com/video123", True),
        ("https://www.XNXX.com/video", True),  # test case-insensitive
        ("https://example.com/watch?v=123", False),
        ("https://youtube.com/watch?v=dQw4w9WgXcQ", False),
        ("random string", False),
    ],
)
def test_is_adult_url(url: str, expected: bool) -> None:
    """Test the is_adult_url function."""
    assert is_adult_url(url) == expected


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.tiktok.com/@username/video/123", True),
        ("https://instagram.com/p/abc123", True),
        ("https://twitter.com/user/status/123456", True),
        ("https://x.com/user/status/654321", True),
        ("https://facebook.com/user/posts/123", True),
        ("https://example.com/watch?v=dQw4w9WgXcQ", False),
        ("https://youtube.com/watch?v=dQw4w9WgXcQ", False),
        ("random string", False),
    ],
)
def test_is_social_url(url: str, expected: bool) -> None:
    """Test the is_social_url function."""
    assert is_social_url(url) == expected


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("percent", "width", "fill", "empty", "expected"),
    [
        (0, 12, "█", "░", "░" * 12),  # 0% progress
        (50, 12, "█", "░", "█" * 6 + "░" * 6),  # 50% progress
        (100, 12, "█", "░", "█" * 12),  # 100% progress
        # 25% progress with smaller width
        (25, 8, "█", "░", "█" * 2 + "░" * 6),
        (110, 10, "█", "░", "█" * 10),  # >100% should be clamped
        (-20, 10, "█", "░", "░" * 10),  # <0% should be clamped
        # custom fill/empty characters
        (50, 10, "#", "-", "#" * 5 + "-" * 5),
        # fractional width rounding down
        (33, 9, "■", ".", "■" * 2 + "." * 7),
        (66, 9, "■", ".", "■" * 5 + "." * 4),  # another fractional case
    ],
)
def test_make_bar(percent: float, width: int, fill: str, empty: str, expected: str) -> None:
    """Test make_bar with various percentages, widths, and characters."""
    assert make_bar(percent, width, fill, empty) == expected
