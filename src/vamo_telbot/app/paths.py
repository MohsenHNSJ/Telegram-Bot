"""Stores paths required by the app."""

from pathlib import Path

SECRETS_FILE_PATH: Path = Path(__file__).resolve().parent.parent.parent.parent / "secrets.json"
"""Path to the JSON file storing secret configurations."""
