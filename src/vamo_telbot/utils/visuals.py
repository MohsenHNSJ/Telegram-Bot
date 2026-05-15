"""Visuals utilities for the Telegram bot."""


def make_bar(percent: float, width: int = 12, fill: str = "█", empty: str = "░") -> str:
    """Generate a simple text progress bar.

    Args:
        percent (float): Progress percentage (0-100).
        width (int): Total width of the bar.
        fill (str): Character to represent filled progress.
        empty (str): Character to represent empty progress.

    Returns:
        str: Text-based progress bar.
    """
    percent = max(0, min(100, percent))  # clamp to [0, 100]
    filled = int(width * percent / 100)
    return fill * filled + empty * (width - filled)
