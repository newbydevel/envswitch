"""Tests for envswitch.history module."""

import pytest
from pathlib import Path
from envswitch.history import (
    load_history,
    save_history,
    record_apply,
    get_last_applied,
    clear_history,
)


@pytest.fixture
def hist_file(tmp_path):
    return tmp_path / "history.json"


def test_load_history_empty(hist_file):
    result = load_history(hist_file)
    assert result == {}


def test_save_and_load_history(hist_file):
    data = {"/home/user/project": "production", "/home/user/other": "staging"}
    save_history(data, hist_file)
    loaded = load_history(hist_file)
    assert loaded == data


def test_record_apply_creates_entry(hist_file):
    record_apply("dev", directory="/projects/myapp", path=hist_file)
    history = load_history(hist_file)
    assert history["/projects/myapp"] == "dev"


def test_record_apply_overwrites_existing(hist_file):
    record_apply("dev", directory="/projects/myapp", path=hist_file)
    record_apply("staging", directory="/projects/myapp", path=hist_file)
    history = load_history(hist_file)
    assert history["/projects/myapp"] == "staging"


def test_record_apply_multiple_dirs(hist_file):
    record_apply("dev", directory="/projects/a", path=hist_file)
    record_apply("prod", directory="/projects/b", path=hist_file)
    history = load_history(hist_file)
    assert history["/projects/a"] == "dev"
    assert history["/projects/b"] == "prod"


def test_get_last_applied_returns_profile(hist_file):
    record_apply("staging", directory="/projects/myapp", path=hist_file)
    result = get_last_applied(directory="/projects/myapp", path=hist_file)
    assert result == "staging"


def test_get_last_applied_returns_none_if_missing(hist_file):
    result = get_last_applied(directory="/nonexistent/dir", path=hist_file)
    assert result is None


def test_clear_history(hist_file):
    record_apply("dev", directory="/projects/myapp", path=hist_file)
    clear_history(hist_file)
    assert not hist_file.exists()


def test_clear_history_no_file_does_not_raise(hist_file):
    # should not raise even if file doesn't exist
    clear_history(hist_file)
