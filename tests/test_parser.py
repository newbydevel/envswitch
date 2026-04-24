"""Tests for the .env parser module."""

import pytest
from envswitch.parser import parse_env_string, serialize_env


def test_basic_key_value():
    content = "KEY=value\nANOTHER=thing"
    result = parse_env_string(content)
    assert result == {"KEY": "value", "ANOTHER": "thing"}


def test_skips_blank_lines_and_comments():
    content = "\n# this is a comment\nKEY=value\n"
    result = parse_env_string(content)
    assert result == {"KEY": "value"}


def test_double_quoted_value():
    result = parse_env_string('DB_URL="postgres://localhost/mydb"')
    assert result["DB_URL"] == "postgres://localhost/mydb"


def test_single_quoted_value():
    result = parse_env_string("SECRET='my secret value'")
    assert result["SECRET"] == "my secret value"


def test_inline_comment_stripped():
    result = parse_env_string("PORT=8080 # default port")
    assert result["PORT"] == "8080"


def test_empty_value():
    result = parse_env_string("EMPTY=")
    assert result["EMPTY"] == ""


def test_line_without_equals_is_ignored():
    result = parse_env_string("NODEFINITION\nKEY=ok")
    assert "NODEFINITION" not in result
    assert result["KEY"] == "ok"


def test_serialize_basic():
    env = {"KEY": "value", "PORT": "3000"}
    output = serialize_env(env)
    assert "KEY=value" in output
    assert "PORT=3000" in output


def test_serialize_quotes_values_with_spaces():
    env = {"GREETING": "hello world"}
    output = serialize_env(env)
    assert 'GREETING="hello world"' in output


def test_roundtrip():
    original = {"APP_ENV": "production", "SECRET_KEY": "abc123", "PORT": "443"}
    serialized = serialize_env(original)
    parsed = parse_env_string(serialized)
    assert parsed == original
