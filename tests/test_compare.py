"""Tests for envswitch.compare module."""

import pytest
from envswitch.compare import compare_profiles, format_compare_report


@pytest.fixture
def profile_a():
    return {
        "APP_ENV": "development",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


@pytest.fixture
def profile_b():
    return {
        "APP_ENV": "production",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_URL": "https://api.example.com",
    }


def test_shared_keys(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    assert set(report["shared_keys"]) == {"APP_ENV", "DB_HOST", "DB_PORT"}


def test_only_in_a(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    assert report["only_in_a"] == ["SECRET_KEY"]


def test_only_in_b(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    assert report["only_in_b"] == ["API_URL"]


def test_matching_values(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    assert "DB_HOST" in report["matching"]
    assert "DB_PORT" in report["matching"]
    assert "APP_ENV" not in report["matching"]


def test_differing_values(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    differing_keys = [k for k, _, _ in report["differing"]]
    assert "APP_ENV" in differing_keys


def test_differing_contains_both_values(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    entry = next(item for item in report["differing"] if item[0] == "APP_ENV")
    assert entry[1] == "development"
    assert entry[2] == "production"


def test_similarity_score_partial(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    # 2 matching out of 5 unique keys
    assert report["similarity_score"] == round(2 / 5, 4)


def test_similarity_score_identical():
    p = {"A": "1", "B": "2"}
    report = compare_profiles(p, p)
    assert report["similarity_score"] == 1.0


def test_similarity_score_empty_both():
    report = compare_profiles({}, {})
    assert report["similarity_score"] == 1.0


def test_similarity_score_no_overlap():
    report = compare_profiles({"A": "1"}, {"B": "2"})
    assert report["similarity_score"] == 0.0


def test_format_compare_report_contains_names(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    output = format_compare_report("dev", "prod", report)
    assert "dev" in output
    assert "prod" in output


def test_format_compare_report_shows_score(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    output = format_compare_report("dev", "prod", report)
    assert "40%" in output or "Similarity" in output


def test_format_compare_report_shows_differing(profile_a, profile_b):
    report = compare_profiles(profile_a, profile_b)
    output = format_compare_report("dev", "prod", report)
    assert "APP_ENV" in output
    assert "development" in output
    assert "production" in output
