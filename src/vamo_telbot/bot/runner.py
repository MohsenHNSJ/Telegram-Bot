"""Runner module for the Telegram bot."""

from telethon import TelegramClient  # type: ignore[import-untyped]

from vamo_telbot.config.telegram import load_bot_token


async def start_bot(client: TelegramClient) -> None:
    """Runs the Telegram bot.

    Args:
        client (TelegramClient): The Telegram client instance to run the bot with.
    """
    async with client:
        await client.start(  # pyright: ignore[reportGeneralTypeIssues]
            bot_token=load_bot_token(),
        )
        print("Bot started successfully!")
        await client.run_until_disconnected()  # type: ignore[unused-ignore]
