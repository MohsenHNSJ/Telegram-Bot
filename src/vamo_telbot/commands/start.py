"""Start command handler for the Telegram bot."""

from telethon import events  # type: ignore[import-untyped]

_START_COMMAND_REPLY: str = "We can do a lot of things."


async def handle_start(event: events.newmessage.NewMessage.Event) -> None:
    """Handle /start command."""
    await event.reply(_START_COMMAND_REPLY)
