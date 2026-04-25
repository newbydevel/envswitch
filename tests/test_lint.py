"""Tests for envswitch.lint"""

import pytest
from envswitch.lint import lint_profile, lint_all_profiles, LintIssue


def issues_by_key(issues, key):
    return [i for i in issues if i.key == key]


def test_no_issues_for_clean_profile():
    profile = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    assert lint_profile(profile) == []


def test_empty_value_warning():
    issues = lint_profile({"DATABASE_URL": ""})
    assert len(issues) == 1
    assert issues[0].level == "warning"
    assert issues[0].key == "DATABASE_URL"
    assert "empty" in issues[0].message.lower()


def test_sensitive_key_plaintext_warning():
    issues = lint_profile({"API_KEY": "supersecret123"})
    key_issues = issues_by_key(issues, "API_KEY")
    assert any(i.level == "warning" and "sensitive" in i.message.lower() for i in key_issues)


def test_sensitive_key_with_placeholder_no_warning():
    # Value that looks like a reference should not trigger the sensitive warning
    issues = lint_profile({"API_KEY": "${SOME_VAR}"})
    sensitive_issues = [
        i for i in issues_by_key(issues, "API_KEY")
        if "sensitive" in i.message.lower()
    ]
    assert sensitive_issues == []


def test_whitespace_only_value_warning():
    issues = lint_profile({"MY_VAR": "   "})
    assert any(i.level == "warning" and "whitespace" in i.message.lower() for i in issues)


def test_embedded_newline_error():
    issues = lint_profile({"MULTILINE": "line1\nline2"})
    assert any(i.level == "error" and "newline" in i.message.lower() for i in issues)


def test_embedded_carriage_return_error():
    issues = lint_profile({"BAD": "value\rwith\rcr"})
    assert any(i.level == "error" and "newline" in i.message.lower() for i in issues)


def test_long_value_warning():
    long_val = "x" * 1025
    issues = lint_profile({"BIG": long_val})
    assert any(i.level == "warning" and "long" in i.message.lower() for i in issues)


def test_exactly_1024_chars_no_length_warning():
    val = "a" * 1024
    issues = lint_profile({"OK": val})
    length_issues = [i for i in issues if "long" in i.message.lower()]
    assert length_issues == []


def test_lint_all_profiles_returns_per_profile():
    profiles = {
        "dev": {"HOST": "localhost"},
        "prod": {"SECRET_KEY": "hardcoded", "PORT": ""},
    }
    result = lint_all_profiles(profiles)
    assert "dev" in result
    assert "prod" in result
    assert result["dev"] == []
    assert len(result["prod"]) >= 2


def test_lint_all_profiles_empty():
    assert lint_all_profiles({}) == {}


def test_multiple_issues_same_key():
    # A sensitive key with empty value should trigger both sensitive and empty warnings
    issues = lint_profile({"PASSWORD": ""})
    # empty value warning should be present
    assert any("empty" in i.message.lower() for i in issues)
    # sensitive warning should NOT fire because value is empty (no plaintext secret)
    sensitive = [i for i in issues if "sensitive" in i.message.lower()]
    assert sensitive == []
