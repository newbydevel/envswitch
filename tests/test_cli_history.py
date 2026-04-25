"""Tests for the history CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envswitch.cli_history import cmd_history


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, **kwargs):
    return runner.invoke(cmd_history, *args, **kwargs)


def test_history_list_empty(runner):
    with patch("envswitch.cli_history.load_history", return_value={}):
        result = invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "No history recorded yet" in result.output


def test_history_list_with_entries(runner):
    fake_history = {
        "/projects/app": "development",
        "/projects/api": "staging",
    }
    with patch("envswitch.cli_history.load_history", return_value=fake_history):
        result = invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "/projects/app" in result.output
    assert "development" in result.output
    assert "/projects/api" in result.output
    assert "staging" in result.output


def test_history_current_found(runner):
    with patch("envswitch.cli_history.get_last_applied", return_value="production"):
        result = invoke(runner, ["current", "/projects/myapp"])
    assert result.exit_code == 0
    assert "production" in result.output


def test_history_current_not_found(runner):
    with patch("envswitch.cli_history.get_last_applied", return_value=None):
        result = invoke(runner, ["current", "/projects/unknown"])
    assert result.exit_code == 0
    assert "No profile recorded" in result.output


def test_history_current_uses_cwd_by_default(runner):
    with patch("envswitch.cli_history.get_last_applied", return_value="dev") as mock_get:
        result = invoke(runner, ["current"])
    mock_get.assert_called_once_with(directory=None)
    assert result.exit_code == 0
    assert "dev" in result.output


def test_history_clear_confirmed(runner):
    with patch("envswitch.cli_history.clear_history") as mock_clear:
        result = invoke(runner, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert "History cleared" in result.output
    mock_clear.assert_called_once()


def test_history_clear_aborted(runner):
    with patch("envswitch.cli_history.clear_history") as mock_clear:
        result = invoke(runner, ["clear"], input="n\n")
    assert result.exit_code != 0 or "Aborted" in result.output
    mock_clear.assert_not_called()
