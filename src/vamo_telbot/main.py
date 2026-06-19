#!/usr/bin/env python
"""Main module of Telegram Bot."""

# region Imports
import asyncio

from telethon import TelegramClient, events  # type: ignore[import-untyped]

from vamo_telbot.bot.runner import start_bot
from vamo_telbot.commands.start import handle_start
from vamo_telbot.commands.youtube import handle_youtube_download
from vamo_telbot.config.telegram import (
    load_api_hash,
    load_api_id,
)
from vamo_telbot.utils.credentials import ensure_credentials
from vamo_telbot.utils.url_checkers import YOUTUBE_PATTERNS as YT_P

# endregion Imports

# ==================== تنظیمات ====================
SESSION_NAME: str = "telegram_bot"


def create_bot_client() -> TelegramClient:
    """Create the Telegram client instance.

    Returns:
        TelegramClient: A new Telegram client instance.
    """
    return TelegramClient(
        SESSION_NAME,
        load_api_id(),
        load_api_hash(),
    )


async def main() -> None:
    """Main bot loop."""
    print("Telegram bot is starting...")
    print("Checking credentials...")

    needs_restart: bool = await ensure_credentials()

    if needs_restart:
        print("Credentials were updated. Restart the program to apply changes.")
        return

    print("Credentials OK. Starting bot...")
    telegram_bot = create_bot_client()

    @telegram_bot.on(events.NewMessage(pattern=YT_P))  # type: ignore[misc]
    async def youtube_download(event: events.newmessage.NewMessage.Event) -> None:
        await handle_youtube_download(event)

    @telegram_bot.on(events.NewMessage(pattern="/start"))  # type: ignore[misc]
    async def start(event: events.newmessage.NewMessage.Event) -> None:
        await handle_start(event)

    await start_bot(telegram_bot)


if __name__ == "__main__":
    asyncio.run(main())
