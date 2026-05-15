"""Telegram Bot configuration.

Handles loading and saving the Bot configuration and secrets.
"""

from __future__ import annotations

from typing import Final

from vamo_telbot.config.manager import get_config_value, set_config_value

# Keys
_API_ID_KEY: Final[str] = "api_id"
_API_HASH_KEY: Final[str] = "api_hash"
_BOT_TOKEN_KEY: Final[str] = "bot_token"  # noqa: S105
# Not defined constants
HASH_OR_TOKEN_NOT_SET: Final[str] = "NOT_SET"  # noqa: S105
ID_NOT_SET: Final[int] = 1

# region API ID


def load_api_id() -> int:
    """Load the telegram API ID from the configuration file.

    Returns:
        The stored API ID if present, otherwise ``ID_NOT_SET``.
    """
    # Get the API ID
    api_id: int | None = get_config_value(_API_ID_KEY)

    # If it's an integer and valid return it
    if isinstance(api_id, int):
        return api_id

    # Else return 1
    return ID_NOT_SET


def save_api_id(api_id: int) -> None:
    """Persist the API ID into the configuration file.

    Args:
        api_id: API ID to store.
    """
    set_config_value(_API_ID_KEY, api_id)


# endregion API ID

# region API HASH


def load_api_hash() -> str:
    """Load the telegram API HASH from the configuration file.

    Returns:
        The stored API HASH if present, otherwise ``HASH_OR_TOKEN_NOT_SET``.
    """
    # Get the API HASH
    api_hash: str | None = get_config_value(_API_HASH_KEY)

    # If it's a string and valid return it
    if isinstance(api_hash, str):
        return api_hash

    # Else return "HASH_OR_TOKEN_NOT_SET"
    return HASH_OR_TOKEN_NOT_SET


def save_api_hash(api_hash: str) -> None:
    """Persist the API HASH into the configuration file.

    Args:
        api_hash: API HASH to store.
    """
    set_config_value(_API_HASH_KEY, api_hash)


# endregion API HASH

# region BOT TOKEN


def load_bot_token() -> str:
    """Load the telegram Bot Token from the configuration file.

    Returns:
        The stored Bot Token if present, otherwise ``HASH_OR_TOKEN_NOT_SET``.
    """
    # Get the Bot Token
    bot_token = get_config_value(_BOT_TOKEN_KEY)

    # If it's a string and valid return it
    if isinstance(bot_token, str):
        return bot_token

    # Else return ``HASH_OR_TOKEN_NOT_SET``
    return HASH_OR_TOKEN_NOT_SET


def save_bot_token(bot_token: str) -> None:
    """Persist the Bot Token into the configuration file.

    Args:
        bot_token: Bot Token to store.
    """
    set_config_value(_BOT_TOKEN_KEY, bot_token)


# endregion BOT TOKEN
