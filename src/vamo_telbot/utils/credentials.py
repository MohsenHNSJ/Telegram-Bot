"""Credential management utilities for the Telegram bot."""

from vamo_telbot.config.telegram import (
    HASH_OR_TOKEN_NOT_SET,
    ID_NOT_SET,
    load_api_hash,
    load_api_id,
    load_bot_token,
    save_api_hash,
    save_api_id,
    save_bot_token,
)


async def ensure_credentials() -> bool:
    """Ensures that all necessary credentials (API ID, API Hash, Bot Token) are set.

    Returns:
        bool: True if any credentials were missing and had to be set, False otherwise.
    """
    needs_reload = False

    if load_api_id() == ID_NOT_SET:
        api_id = int(input("API ID not found. Please enter it: ").strip())  # noqa: ASYNC250
        save_api_id(api_id)
        needs_reload = True

    if load_api_hash() == HASH_OR_TOKEN_NOT_SET:
        api_hash = input("API HASH not found. Please enter it: ").strip()  # noqa: ASYNC250
        save_api_hash(api_hash)
        needs_reload = True

    if load_bot_token() == HASH_OR_TOKEN_NOT_SET:
        bot_token = input("Bot Token not found. Please enter it: ").strip()  # noqa: ASYNC250
        save_bot_token(bot_token)

    return needs_reload
