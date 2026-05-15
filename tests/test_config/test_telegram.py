"""Tests for telegram config module."""

# ruff: noqa: S101, ANN401
from typing import Any
from unittest.mock import patch

import pytest

from vamo_telbot.config.telegram import (
    _API_HASH_KEY,
    _API_ID_KEY,
    _BOT_TOKEN_KEY,
    load_api_hash,
    load_api_id,
    load_bot_token,
    save_api_hash,
    save_api_id,
    save_bot_token,
)


@pytest.mark.parametrize(
    ("mock_return", "expected"),
    [
        (12345, 12345),  # valid integer from config
        ("12345", 1),  # string instead of int → fallback
        (None, 1),  # missing key → fallback
        ([], 1),  # invalid type → fallback
    ],
)
def test_load_api_id(mock_return: Any, expected: int) -> None:
    """Test the load_api_id function."""
    # Patch get_config_value to return different test values
    with patch(
        "vamo_telbot.config.telegram.get_config_value",
        return_value=mock_return,
    ) as mock_func:
        assert load_api_id() == expected
        mock_func.assert_called_once_with(_API_ID_KEY)


@pytest.mark.parametrize(
    "api_id",
    [
        12345,
        0,
        99999999,
    ],
)
def test_save_api_id(api_id: int) -> None:
    """Test the save_api_id function."""
    # Patch set_config_value where save_api_id uses it
    with patch("vamo_telbot.config.telegram.set_config_value") as mock_func:
        save_api_id(api_id)
        # Ensure set_config_value was called once with correct arguments
        mock_func.assert_called_once_with(_API_ID_KEY, api_id)


@pytest.mark.parametrize(
    ("mock_return", "expected"),
    [
        ("ABC123XYZ", "ABC123XYZ"),  # valid string returned
        (12345, "NOT_SET"),  # invalid type → fallback
        (None, "NOT_SET"),  # missing key → fallback
        ([], "NOT_SET"),  # invalid type → fallback
    ],
)
def test_load_api_hash(mock_return: Any, expected: str) -> None:
    """Test the load_api_hash function."""
    # Patch where load_api_hash uses get_config_value
    with patch(
        "vamo_telbot.config.telegram.get_config_value",
        return_value=mock_return,
    ) as mock_func:
        assert load_api_hash() == expected
        mock_func.assert_called_once_with(_API_HASH_KEY)


@pytest.mark.parametrize(
    "api_hash",
    [
        "ABC123XYZ",
        "another_hash",
        "",
    ],
)
def test_save_api_hash(api_hash: str) -> None:
    """Test the save_api_hash function."""
    # Patch set_config_value where save_api_hash uses it
    with patch("vamo_telbot.config.telegram.set_config_value") as mock_func:
        save_api_hash(api_hash)
        # Ensure set_config_value was called once with correct arguments
        mock_func.assert_called_once_with(_API_HASH_KEY, api_hash)


@pytest.mark.parametrize(
    ("mock_return", "expected"),
    [
        ("123456:ABCDEF", "123456:ABCDEF"),  # valid token string
        (123456, None),  # invalid type → fallback
        (None, None),  # missing key → fallback
        ([], None),  # invalid type → fallback
    ],
)
def test_load_bot_token(mock_return: Any, expected: str) -> None:
    """Test the load_bot_token function."""
    # Patch where load_bot_token uses get_config_value
    with patch(
        "vamo_telbot.config.telegram.get_config_value",
        return_value=mock_return,
    ) as mock_func:
        assert load_bot_token() == expected
        mock_func.assert_called_once_with(_BOT_TOKEN_KEY)


@pytest.mark.parametrize(
    "bot_token",
    [
        "123456:ABCDEF",
        "987654:AAAAA",
        "",
    ],
)
def test_save_bot_token(bot_token: str) -> None:
    """Test the save_bot_token function."""
    # Patch set_config_value where save_bot_token uses it
    with patch("vamo_telbot.config.telegram.set_config_value") as mock_func:
        save_bot_token(bot_token)
        # Ensure set_config_value was called once with correct arguments
        mock_func.assert_called_once_with(_BOT_TOKEN_KEY, bot_token)
