"""Tests for utility functions."""

# ruff: noqa: S101, FBT001
import pytest

from vamo_telbot.utils import is_youtube_url


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
