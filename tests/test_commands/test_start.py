"""Tests the start command module."""

from unittest.mock import AsyncMock

import pytest

from vamo_telbot.commands.start import _START_COMMAND_REPLY, handle_start


@pytest.mark.asyncio
async def test_handle_start_calls_reply() -> None:
    """Test that handle_start calls the reply method with the correct message."""
    # Create a mock event with async reply method
    mock_event = AsyncMock()

    # Call the handler
    await handle_start(mock_event)

    # Ensure reply was called once with the expected message
    mock_event.reply.assert_awaited_once_with(_START_COMMAND_REPLY)
