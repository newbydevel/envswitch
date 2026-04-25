"""Tests for envswitch.merge module."""

import pytest
from envswitch.merge import merge_profiles, merge_profile_names, MergeConflictError


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
OVERRIDE = {"PORT": "9999", "NEW_KEY": "hello"}


def test_merge_theirs_default():
    result = merge_profiles(BASE, OVERRIDE)
    assert result["PORT"] == "9999"
    assert result["HOST"] == "localhost"
    assert result["NEW_KEY"] == "hello"
    assert result["DEBUG"] == "true"


def test_merge_ours_keeps_base_on_conflict():
    result = merge_profiles(BASE, OVERRIDE, strategy="ours")
    assert result["PORT"] == "5432"  # base wins
    assert result["NEW_KEY"] == "hello"  # new key still added
    assert result["HOST"] == "localhost"


def test_merge_error_raises_on_conflict():
    with pytest.raises(MergeConflictError) as exc_info:
        merge_profiles(BASE, OVERRIDE, strategy="error")
    assert "PORT" in exc_info.value.conflicts


def test_merge_error_no_conflict_succeeds():
    no_conflict = {"NEW_KEY": "hello", "ANOTHER": "world"}
    result = merge_profiles(BASE, no_conflict, strategy="error")
    assert result["NEW_KEY"] == "hello"
    assert result["ANOTHER"] == "world"
    assert result["HOST"] == "localhost"


def test_merge_identical_values_not_a_conflict():
    same = {"HOST": "localhost"}  # same value, not a conflict
    result = merge_profiles(BASE, same, strategy="error")
    assert result["HOST"] == "localhost"


def test_merge_empty_override():
    result = merge_profiles(BASE, {})
    assert result == BASE


def test_merge_empty_base():
    result = merge_profiles({}, OVERRIDE)
    assert result == OVERRIDE


def test_merge_profile_names_success():
    profiles = {"dev": BASE, "staging": OVERRIDE}
    result = merge_profile_names(profiles, "dev", "staging", strategy="theirs")
    assert result["PORT"] == "9999"
    assert result["HOST"] == "localhost"


def test_merge_profile_names_missing_base():
    with pytest.raises(KeyError, match="base_profile"):
        merge_profile_names({"other": {}}, "base_profile", "other")


def test_merge_profile_names_missing_override():
    with pytest.raises(KeyError, match="missing"):
        merge_profile_names({"dev": BASE}, "dev", "missing")


def test_merge_conflict_error_message():
    err = MergeConflictError(["PORT", "HOST"])
    assert "PORT" in str(err)
    assert "HOST" in str(err)
