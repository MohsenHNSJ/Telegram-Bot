"""Tests for config manager module."""

# ruff: noqa: S101, ANN401
import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from vamo_telbot.config.manager import get_config_value, load_config, save_config, set_config_value


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("exists", "read_text_return", "read_text_side_effect", "expected"),
    [
        (False, None, None, {}),  # file does not exist
        (True, '{"key": "value"}', None, {"key": "value"}),  # valid JSON dict
        # JSON is valid but not a dict
        (True, '["not","a","dict"]', None, {}),
        # reading file raises OSError
        (True, None, OSError, {}),
        # invalid JSON raises JSONDecodeError
        (True, "{invalid json}", None, {}),
    ],
)
def test_load_config(
    *,
    exists: bool,
    read_text_return: Any,
    read_text_side_effect: Any,
    expected: dict[str, Any],
) -> None:
    """Test load_config with various file states and contents."""
    mock_path = MagicMock()
    mock_path.exists.return_value = exists

    if read_text_side_effect:
        mock_path.read_text.side_effect = read_text_side_effect
    elif read_text_return is not None:
        mock_path.read_text.return_value = read_text_return
    else:
        mock_path.read_text.return_value = None

    # Patch SECRETS_FILE_PATH to use our mock path
    with patch("vamo_telbot.config.manager.SECRETS_FILE_PATH", mock_path):
        result: dict[str, Any] = load_config()
        assert result == expected


@pytest.mark.benchmark
@pytest.mark.parametrize(
    "config_data",
    [
        {},  # empty dict
        {"key": "value"},  # simple dict
        {"number": 123, "list": [1, 2]},  # complex dict
    ],
)
def test_save_config(config_data: dict[str, str] | dict[str, int | list[int]]) -> None:
    """Test save_config writes correct JSON to disk."""
    # Mock SECRETS_FILE_PATH
    mock_path = MagicMock()

    with patch("vamo_telbot.config.manager.SECRETS_FILE_PATH", mock_path):
        save_config(config_data)

        # Ensure write_text is called once
        mock_path.write_text.assert_called_once()

        # Check that the written text is the pretty-printed JSON
        args, kwargs = mock_path.write_text.call_args
        written_text = args[0]  # first positional argument
        encoding = kwargs.get("encoding", None)

        expected_text = json.dumps(config_data, ensure_ascii=False, indent=2)

        assert written_text == expected_text
        assert encoding == "utf-8"


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("existing_config", "key", "value", "expected_config"),
    [
        (
            {},
            "new_key",
            "value",
            {"new_key": "value"},
        ),  # empty config
        # add new key
        ({"a": 1}, "b", 2, {"a": 1, "b": 2}),
        # update existing key
        ({"a": 1}, "a", 42, {"a": 42}),
        (
            {"nested": {"x": 1}},
            "nested",
            {"y": 2},
            {
                "nested": {"y": 2},
            },
        ),  # replace nested
    ],
)
def test_set_config_value(
    existing_config: dict[str, Any],
    key: str,
    value: Any,
    expected_config: dict[str, Any],
) -> None:
    """Test set_config_value updates config correctly and saves it."""
    # Mock load_config to return existing_config
    with (
        patch(
            "vamo_telbot.config.manager.load_config",
            return_value=existing_config,
        ) as mock_load,
        patch("vamo_telbot.config.manager.save_config") as mock_save,
    ):
        set_config_value(key, value)

        # Ensure load_config is called once
        mock_load.assert_called_once()

        # Ensure save_config is called with the updated config
        mock_save.assert_called_once_with(expected_config)


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("mock_config", "key", "default", "expected"),
    [
        ({"a": 1, "b": 2}, "a", None, 1),  # key exists
        # key exists with default provided
        ({"a": 1, "b": 2}, "b", 0, 2),
        # key missing, default None
        ({"a": 1}, "missing", None, None),
        # key missing, default provided
        ({"a": 1}, "missing", "default", "default"),
        # empty config, return default
        ({}, "any", 42, 42),
    ],
)
def test_get_config_value(
    mock_config: dict[str, Any],
    key: str,
    default: Any,
    expected: Any,
) -> None:
    """Test get_config_value retrieves correct value or default."""
    with patch("vamo_telbot.config.manager.load_config", return_value=mock_config) as mock_load:
        result = get_config_value(key, default)
        assert result == expected
        mock_load.assert_called_once()
