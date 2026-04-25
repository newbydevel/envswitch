"""Tests for envswitch/cli_audit.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envswitch.cli_audit import cmd_audit


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, **kwargs):
    return runner.invoke(cmd_audit, list(args), catch_exceptions=False, **kwargs)


def _make_entry(ts, action, profile, details=None):
    e = {"timestamp": ts, "action": action, "profile": profile}
    if details:
        e["details"] = details
    return e


def test_audit_list_empty(runner):
    with patch("envswitch.cli_audit.load_audit", return_value=[]):
        with patch("envswitch.cli_audit.get_audit_path", return_value=MagicMock()):
            result = invoke(runner, "list")
    assert result.exit_code == 0
    assert "No audit entries found" in result.output


def test_audit_list_shows_entries(runner):
    entries = [
        _make_entry("2024-06-01T10:00:00+00:00", "apply", "dev"),
        _make_entry("2024-06-02T11:00:00+00:00", "delete", "staging"),
    ]
    with patch("envswitch.cli_audit.load_audit", return_value=entries):
        with patch("envswitch.cli_audit.get_audit_path", return_value=MagicMock()):
            result = invoke(runner, "list")
    assert "apply -> dev" in result.output
    assert "delete -> staging" in result.output


def test_audit_list_filter_by_profile(runner):
    entries = [_make_entry("2024-06-01T10:00:00+00:00", "apply", "dev")]
    with patch("envswitch.cli_audit.get_events_for_profile", return_value=entries):
        with patch("envswitch.cli_audit.get_audit_path", return_value=MagicMock()):
            result = invoke(runner, "list", "--profile", "dev")
    assert "apply -> dev" in result.output


def test_audit_list_shows_details(runner):
    entries = [
        _make_entry("2024-06-01T10:00:00+00:00", "rename", "dev", details={"new_name": "dev2"}),
    ]
    with patch("envswitch.cli_audit.load_audit", return_value=entries):
        with patch("envswitch.cli_audit.get_audit_path", return_value=MagicMock()):
            result = invoke(runner, "list")
    assert "new_name=dev2" in result.output


def test_audit_clear(runner):
    mock_clear = MagicMock()
    with patch("envswitch.cli_audit.clear_audit", mock_clear):
        with patch("envswitch.cli_audit.get_audit_path", return_value=MagicMock()):
            result = runner.invoke(cmd_audit, ["clear"], input="y\n", catch_exceptions=False)
    assert result.exit_code == 0
    assert "cleared" in result.output
    mock_clear.assert_called_once()
