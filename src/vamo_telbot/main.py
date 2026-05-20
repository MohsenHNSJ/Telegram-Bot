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

telegram_bot: TelegramClient = TelegramClient(
    SESSION_NAME,
    load_api_id(),
    load_api_hash(),
)


# Main menu actions


@telegram_bot.on(events.NewMessage(pattern=YT_P))  # type: ignore[misc]
async def youtube_download(event: events.newmessage.NewMessage.Event) -> None:
    """Handle incoming YouTube links and trigger the download process.

    Args:
        event (events.newmessage.NewMessage.Event): The event triggered by a new message,
            containing a YouTube link.
    """
    await handle_youtube_download(event)


@telegram_bot.on(events.NewMessage(pattern="/start"))  # type: ignore[misc]
async def start(event: events.newmessage.NewMessage.Event) -> None:
    """Handle the /start command from users.

    Args:
        event (events.newmessage.NewMessage.Event): The event triggered by the /start command.
    """
    await handle_start(event)


async def main() -> None:
    """Main bot loop."""
    print("Telegram bot is starting...")
    print("Checking credentials...")

    needs_restart: bool = await ensure_credentials()

    if needs_restart:
        print("Credentials were updated. Restart the program to apply changes.")
        return

    print("Credentials OK. Starting bot...")
    await start_bot(telegram_bot)


if __name__ == "__main__":
    asyncio.run(main())
