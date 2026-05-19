"""Tests for the credentials management utilities."""

# ruff: noqa: S101
from typing import Any
from unittest.mock import patch

import pytest

from vamo_telbot.config.telegram import HASH_OR_TOKEN_NOT_SET, ID_NOT_SET
from vamo_telbot.utils.credentials import ensure_credentials


@pytest.mark.benchmark
@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "api_id_val",
        "api_hash_val",
        "bot_token_val",
        "input_values",
        "expected_reload",
    ),
    [
        (
            ID_NOT_SET,
            HASH_OR_TOKEN_NOT_SET,
            HASH_OR_TOKEN_NOT_SET,
            [
                "11111",
                "hash123",
                "token123",
            ],
            True,
        ),  # all missing
        (12345, "hash123", "token123", [], False),  # all present
        # only API ID missing
        (ID_NOT_SET, "hash123", "token123", ["11111"], True),
        # only API HASH missing
        (12345, HASH_OR_TOKEN_NOT_SET, "token123", ["hash123"], True),
        # only Bot Token missing
        (12345, "hash123", HASH_OR_TOKEN_NOT_SET, ["token123"], False),
    ],
)
async def test_ensure_credentials(
    *,
    api_id_val: int,
    api_hash_val: str,
    bot_token_val: str | None,
    input_values: list[Any],
    expected_reload: bool,
) -> None:
    """Test the ensure_credentials function with various scenarios of missing credentials."""
    # Mock input to return values from input_values in order
    input_iter = iter(input_values)
    with (
        patch("builtins.input", side_effect=lambda _: next(input_iter)) as _,
        patch("vamo_telbot.utils.credentials.load_api_id", return_value=api_id_val) as _,
        patch("vamo_telbot.utils.credentials.load_api_hash", return_value=api_hash_val) as _,
        patch(
            "vamo_telbot.utils.credentials.load_bot_token",
            return_value=bot_token_val,
        ) as _,
        patch("vamo_telbot.utils.credentials.save_api_id") as mock_save_id,
        patch("vamo_telbot.utils.credentials.save_api_hash") as mock_save_hash,
        patch("vamo_telbot.utils.credentials.save_bot_token") as mock_save_token,
    ):
        result: bool = await ensure_credentials()

        assert result == expected_reload

        # Ensure save functions are called correctly
        if api_id_val == ID_NOT_SET:
            mock_save_id.assert_called_once_with(int(input_values[0]))
        else:
            mock_save_id.assert_not_called()

        if api_hash_val == HASH_OR_TOKEN_NOT_SET:
            mock_save_hash.assert_called_once_with(
                input_values[1 if api_id_val == 1 else 0],
            )
        else:
            mock_save_hash.assert_not_called()

        if bot_token_val == HASH_OR_TOKEN_NOT_SET:
            mock_save_token.assert_called_once_with(input_values[-1])
        else:
            mock_save_token.assert_not_called()
