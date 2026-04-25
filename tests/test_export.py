"""Tests for envswitch.export module."""

import json
import pytest
from envswitch.export import export_profile, export_as_bash, export_as_fish, export_as_dotenv, export_as_json


SAMPLE_VARS = {
    "APP_ENV": "production",
    "DB_URL": "postgres://localhost/mydb",
    "SECRET": 'has "quotes" inside',
    "SPACED": "hello world",
}


def test_bash_export_basic():
    result = export_as_bash({"FOO": "bar"})
    assert result == 'export FOO="bar"'


def test_bash_export_escapes_quotes():
    result = export_as_bash({"MSG": 'say "hi"'})
    assert 'export MSG="say \\"hi\\""' == result


def test_bash_export_multiple_vars():
    result = export_as_bash({"A": "1", "B": "2"})
    lines = result.splitlines()
    assert len(lines) == 2
    assert 'export A="1"' in lines
    assert 'export B="2"' in lines


def test_fish_export_basic():
    result = export_as_fish({"FOO": "bar"})
    assert result == 'set -x FOO "bar"'


def test_fish_export_escapes_quotes():
    result = export_as_fish({"K": 'val"ue'})
    assert '\\"' in result


def test_dotenv_no_quotes_for_simple_values():
    result = export_as_dotenv({"KEY": "simple"})
    assert result == "KEY=simple"


def test_dotenv_quotes_values_with_spaces():
    result = export_as_dotenv({"KEY": "hello world"})
    assert result == 'KEY="hello world"'


def test_dotenv_quotes_values_with_hash():
    result = export_as_dotenv({"KEY": "val#ue"})
    assert result.startswith('KEY="')


def test_json_export_valid_json():
    result = export_as_json({"A": "1", "B": "2"})
    parsed = json.loads(result)
    assert parsed == {"A": "1", "B": "2"}


def test_export_profile_bash():
    result = export_profile({"X": "y"}, "bash")
    assert 'export X="y"' in result


def test_export_profile_fish():
    result = export_profile({"X": "y"}, "fish")
    assert 'set -x X "y"' in result


def test_export_profile_dotenv():
    result = export_profile({"X": "y"}, "dotenv")
    assert "X=y" in result


def test_export_profile_json():
    result = export_profile({"X": "y"}, "json")
    assert json.loads(result) == {"X": "y"}


def test_export_profile_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_profile({"X": "y"}, "toml")
