"""Tests for URL checker utilities."""

# ruff: noqa: S101, FBT001
import pytest

from vamo_telbot.utils.url_checkers import is_adult_url, is_social_url, is_youtube_url


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
