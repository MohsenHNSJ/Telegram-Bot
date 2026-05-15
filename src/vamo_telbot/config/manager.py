"""Centralized application configuration manager."""

from __future__ import annotations

import json
from typing import Any

from vamo_telbot.app.paths import SECRETS_FILE_PATH


def load_config() -> dict[str, Any]:
    """Load application configuration from disk.

    Reads the application configuration file defined by ``SECRETS_FILE_PATH``
    and returns its contents as a dictionary. If the configuration file does
    not exist, cannot be read, contains invalid JSON, or does not represent
    a JSON object, an empty dictionary is returned.

    This function is intentionally defensive and guarantees that the return
    value is always a dictionary, making it safe to use as a mutable
    configuration store by callers.

    Returns:
        dict[str, Any]: A dictionary containing configuration key-value pairs
        loaded from disk, or an empty dictionary if the configuration file is
        missing, invalid, or unreadable.
    """
    # If configuration file does not exist, return empty dictionary
    if not SECRETS_FILE_PATH.exists():
        return {}

    # Try to read the configuration file, on error return empty dictionary
    try:
        config_data = json.loads(SECRETS_FILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    # If the data is a dictionary, return it, else return empty dictionary
    if isinstance(config_data, dict):
        return config_data

    return {}


def save_config(config: dict[str, Any]) -> None:
    """Persist application configuration to disk.

    Serializes the provided configuration dictionary as JSON and writes it
    to the configuration file defined by ``SECRETS_FILE_PATH``. The file is
    written using UTF-8 encoding and pretty-printed formatting to remain
    human-readable.

    This function overwrites the existing configuration file content.
    Callers are expected to load the current configuration, modify only
    the required keys, and then save the updated dictionary.

    Args:
        config: A dictionary containing application configuration
            key-value pairs to persist.
    """
    # Over-write the configuration file
    SECRETS_FILE_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def set_config_value(key: str, value: Any) -> None:  # noqa: ANN401
    """Set a single configuration value and persist it to disk.

    Loads the existing application configuration, adds or updates the
    specified key with the provided value, and writes the updated
    configuration back to the configuration file.

    This function preserves all other existing configuration entries by
    performing a read-modify-write cycle.

    Args:
        key: Configuration key to add or update.
        value: Value to associate with the given key. The value must be
            JSON-serializable.
    """
    # Load the configuration file
    config: dict[str, Any] = load_config()
    # Add or Replace the desired key
    config[key] = value
    # Over-write the configuration file
    save_config(config)


def get_config_value(key: str, default: Any = None) -> Any:  # noqa: ANN401
    """Retrieve a configuration value by key.

    Loads the application configuration from disk and returns the value
    associated with the specified key. If the key does not exist or the
    configuration file is missing or invalid, the provided default value
    is returned.

    Args:
        key: Configuration key to retrieve.
        default: Value to return if the key is not present in the
            configuration. Defaults to ``None``.

    Returns:
        The value associated with the given key if it exists; otherwise,
        the provided default value.
    """
    # Return the requested value of the key
    return load_config().get(key, default)
