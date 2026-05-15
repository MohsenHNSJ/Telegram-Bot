"""Test module for the bot runner."""

from typing import Final
from unittest.mock import AsyncMock, patch

import pytest
from telethon import TelegramClient  # type: ignore[import-untyped]

from vamo_telbot.bot.runner import start_bot

_FAKE_BOT_TOKEN: Final[str] = "fake_bot_token"  # noqa: S105


@pytest.mark.asyncio
async def test_start_bot_runs_methods() -> None:
    """Tests that start_bot.

    Calls the expected methods on the TelegramClient and loads the bot token.
    """
    # Create a mock TelegramClient
    mock_client = AsyncMock(spec=TelegramClient)

    # Properly mock async context manager behavior
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    # Explicitly make start and run_until_disconnected awaitable
    mock_client.start = AsyncMock()
    mock_client.run_until_disconnected = AsyncMock()

    # Mock load_bot_token to return a fake token
    with (
        patch(
            "vamo_telbot.bot.runner.load_bot_token",
            return_value=_FAKE_BOT_TOKEN,
        ) as mock_load_token,
        patch("builtins.print") as mock_print,
    ):
        await start_bot(mock_client)

        # Ensure client.start is called with the token
        mock_client.start.assert_awaited_once_with(bot_token=_FAKE_BOT_TOKEN)

        # Ensure run_until_disconnected is awaited
        mock_client.run_until_disconnected.assert_awaited_once()

        # Ensure print was called
        mock_print.assert_called_once_with("Bot started successfully!")

        # Ensure load_bot_token was called
        mock_load_token.assert_called_once()
