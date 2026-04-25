import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envswitch.cli_diff import cmd_diff


PROFILES = {
    "dev": {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"},
    "prod": {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "info"},
    "empty": {},
}


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, **kwargs):
    with patch("envswitch.cli_diff.load_profiles", return_value=PROFILES):
        return runner.invoke(cmd_diff, list(args), **kwargs)


def test_diff_shows_added(runner):
    result = invoke(runner, "dev", "prod", "--no-color")
    assert result.exit_code == 0
    assert "+ LOG_LEVEL=info" in result.output


def test_diff_shows_removed(runner):
    result = invoke(runner, "dev", "prod", "--no-color")
    assert "- DEBUG=true" in result.output


def test_diff_shows_changed(runner):
    result = invoke(runner, "dev", "prod", "--no-color")
    assert "~ HOST" in result.output


def test_diff_summary_line(runner):
    result = invoke(runner, "dev", "prod", "--no-color")
    assert "added" in result.output
    assert "removed" in result.output
    assert "changed" in result.output


def test_diff_identical_profiles(runner):
    result = invoke(runner, "dev", "dev", "--no-color")
    assert result.exit_code == 0
    assert "No differences." in result.output


def test_diff_missing_profile_a(runner):
    result = invoke(runner, "nope", "prod", "--no-color")
    assert result.exit_code == 1
    assert "nope" in result.output


def test_diff_missing_profile_b(runner):
    result = invoke(runner, "dev", "ghost", "--no-color")
    assert result.exit_code == 1
    assert "ghost" in result.output


def test_diff_both_missing(runner):
    result = invoke(runner, "x", "y", "--no-color")
    assert result.exit_code == 1
