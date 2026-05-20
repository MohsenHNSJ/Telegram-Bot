"""Tests for visual utilities."""

# ruff: noqa: S101,
import pytest

from vamo_telbot.utils.visuals import make_bar


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
