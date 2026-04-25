"""Tests for envswitch.search module."""

import pytest
from envswitch.search import search_profiles, search_by_profile, find_key_across_profiles


@pytest.fixture
def profiles():
    return {
        "dev": {
            "DATABASE_URL": "postgres://localhost/dev",
            "DEBUG": "true",
            "SECRET_KEY": "dev-secret",
        },
        "prod": {
            "DATABASE_URL": "postgres://prod-host/mydb",
            "DEBUG": "false",
            "SECRET_KEY": "super-secret-prod",
            "API_KEY": "abc123",
        },
        "staging": {
            "DATABASE_URL": "postgres://staging-host/stagingdb",
            "DEBUG": "false",
        },
    }


def test_search_matches_key(profiles):
    results = search_profiles(profiles, "API_KEY")
    assert "prod" in results
    assert "API_KEY" in results["prod"]
    assert "dev" not in results


def test_search_matches_value(profiles):
    results = search_profiles(profiles, "prod-host")
    assert "prod" in results
    assert "DATABASE_URL" in results["prod"]


def test_search_key_only_skips_value_match(profiles):
    results = search_profiles(profiles, "prod-host", key_only=True)
    assert results == {}


def test_search_case_insensitive(profiles):
    results = search_profiles(profiles, "debug")
    assert "dev" in results
    assert "prod" in results


def test_search_no_match(profiles):
    results = search_profiles(profiles, "NONEXISTENT_XYZ")
    assert results == {}


def test_search_by_profile_found(profiles):
    results = search_by_profile(profiles, "secret", "dev")
    assert "SECRET_KEY" in results


def test_search_by_profile_not_found_profile(profiles):
    results = search_by_profile(profiles, "anything", "ghost")
    assert results == {}


def test_search_by_profile_no_match(profiles):
    results = search_by_profile(profiles, "API_KEY", "dev")
    assert results == {}


def test_find_key_across_profiles_exact(profiles):
    results = find_key_across_profiles(profiles, "DEBUG")
    assert set(results.keys()) == {"dev", "prod", "staging"}
    assert results["dev"] == "true"
    assert results["prod"] == "false"


def test_find_key_across_profiles_case_insensitive(profiles):
    results = find_key_across_profiles(profiles, "debug")
    assert "dev" in results


def test_find_key_across_profiles_missing(profiles):
    results = find_key_across_profiles(profiles, "TOTALLY_MISSING")
    assert results == {}


def test_find_key_only_in_some_profiles(profiles):
    results = find_key_across_profiles(profiles, "API_KEY")
    assert list(results.keys()) == ["prod"]
    assert results["prod"] == "abc123"
