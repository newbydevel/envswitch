"""Tests for envswitch.validate module."""

import pytest
from envswitch.validate import (
    validate_key,
    validate_profile_name,
    validate_profile,
    assert_valid_profile,
    ValidationError,
)


# --- validate_key ---

def test_valid_keys():
    assert validate_key("FOO") is True
    assert validate_key("MY_VAR") is True
    assert validate_key("_PRIVATE") is True
    assert validate_key("camelCase") is True
    assert validate_key("VAR123") is True


def test_invalid_keys():
    assert validate_key("") is False
    assert validate_key("1STARTS_WITH_DIGIT") is False
    assert validate_key("HAS-DASH") is False
    assert validate_key("HAS SPACE") is False
    assert validate_key("HAS.DOT") is False


# --- validate_profile_name ---

def test_valid_profile_names():
    assert validate_profile_name("dev") is True
    assert validate_profile_name("prod") is True
    assert validate_profile_name("staging-2") is True
    assert validate_profile_name("my_env") is True


def test_invalid_profile_names():
    assert validate_profile_name("") is False
    assert validate_profile_name("has space") is False
    assert validate_profile_name("has.dot") is False
    assert validate_profile_name("has@symbol") is False


# --- validate_profile ---

def test_validate_profile_valid():
    errors = validate_profile("dev", {"DB_HOST": "localhost", "PORT": "5432"})
    assert errors == []


def test_validate_profile_bad_name():
    errors = validate_profile("bad name!", {"FOO": "bar"})
    assert len(errors) == 1
    assert "Invalid profile name" in errors[0]


def test_validate_profile_bad_key():
    errors = validate_profile("dev", {"1INVALID": "value", "VALID": "ok"})
    assert len(errors) == 1
    assert "1INVALID" in errors[0]


def test_validate_profile_multiple_errors():
    errors = validate_profile("bad name", {"1BAD": "x", "also-bad": "y"})
    assert len(errors) == 3  # name + 2 bad keys


def test_validate_profile_non_dict_vars():
    errors = validate_profile("dev", ["not", "a", "dict"])
    assert any("dictionary" in e for e in errors)


# --- assert_valid_profile ---

def test_assert_valid_profile_passes():
    assert_valid_profile("prod", {"API_KEY": "abc"})


def test_assert_valid_profile_raises():
    with pytest.raises(ValidationError) as exc_info:
        assert_valid_profile("bad name", {"1NOPE": "val"})
    assert len(exc_info.value.errors) == 2
