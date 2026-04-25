"""Tests for the validate CLI command."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_validate import cmd_validate


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, profiles=None):
    profiles = profiles or {}
    with patch("envswitch.cli_validate.load_profiles", return_value=profiles):
        return runner.invoke(cmd_validate, list(args))


def test_no_profiles(runner):
    result = invoke(runner, profiles={})
    assert result.exit_code == 0
    assert "No profiles found" in result.output


def test_all_profiles_valid(runner):
    profiles = {
        "dev": {"DB_HOST": "localhost"},
        "prod": {"DB_HOST": "db.prod.example.com"},
    }
    result = invoke(runner, profiles=profiles)
    assert result.exit_code == 0
    assert "[OK]   dev" in result.output
    assert "[OK]   prod" in result.output


def test_single_profile_valid(runner):
    profiles = {"dev": {"FOO": "bar"}}
    result = invoke(runner, "dev", profiles=profiles)
    assert result.exit_code == 0
    assert "[OK]   dev" in result.output


def test_profile_with_invalid_key(runner):
    profiles = {"dev": {"1BAD_KEY": "value", "GOOD": "ok"}}
    result = invoke(runner, profiles=profiles)
    assert result.exit_code == 1
    assert "[FAIL] dev" in result.output
    assert "1BAD_KEY" in result.output


def test_mixed_valid_and_invalid(runner):
    profiles = {
        "dev": {"VALID_VAR": "ok"},
        "broken": {"has-dash": "nope"},
    }
    result = invoke(runner, profiles=profiles)
    assert result.exit_code == 1
    assert "[OK]   dev" in result.output
    assert "[FAIL] broken" in result.output


def test_unknown_profile_name(runner):
    profiles = {"dev": {"FOO": "bar"}}
    result = invoke(runner, "staging", profiles=profiles)
    assert result.exit_code == 1
    assert "not found" in result.output
