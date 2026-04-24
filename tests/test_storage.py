"""Tests for the profile storage module."""

import json
import pytest
from pathlib import Path
from envswitch.storage import (
    load_profiles,
    save_profiles,
    add_profile,
    delete_profile,
    get_profile,
)


@pytest.fixture
def tmp_store(tmp_path):
    """Provide a temporary store directory for each test."""
    return tmp_path / "envswitch_test"


def test_load_profiles_empty(tmp_store):
    result = load_profiles(tmp_store)
    assert result == {}


def test_save_and_load_profiles(tmp_store):
    profiles = {"dev": {"DEBUG": "true", "PORT": "8000"}}
    save_profiles(profiles, tmp_store)
    loaded = load_profiles(tmp_store)
    assert loaded == profiles


def test_add_profile(tmp_store):
    add_profile("staging", {"ENV": "staging"}, store_dir=tmp_store)
    profiles = load_profiles(tmp_store)
    assert "staging" in profiles
    assert profiles["staging"]["ENV"] == "staging"


def test_add_profile_duplicate_raises(tmp_store):
    add_profile("dev", {"KEY": "val"}, store_dir=tmp_store)
    with pytest.raises(ValueError, match="already exists"):
        add_profile("dev", {"KEY": "other"}, store_dir=tmp_store)


def test_add_profile_overwrite(tmp_store):
    add_profile("dev", {"KEY": "old"}, store_dir=tmp_store)
    add_profile("dev", {"KEY": "new"}, store_dir=tmp_store, overwrite=True)
    profile = get_profile("dev", tmp_store)
    assert profile["KEY"] == "new"


def test_delete_profile(tmp_store):
    add_profile("temp", {"X": "1"}, store_dir=tmp_store)
    delete_profile("temp", store_dir=tmp_store)
    profiles = load_profiles(tmp_store)
    assert "temp" not in profiles


def test_delete_missing_profile_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        delete_profile("ghost", store_dir=tmp_store)


def test_get_profile(tmp_store):
    add_profile("prod", {"ENV": "production"}, store_dir=tmp_store)
    profile = get_profile("prod", tmp_store)
    assert profile == {"ENV": "production"}


def test_get_missing_profile_raises(tmp_store):
    with pytest.raises(KeyError, match="not found"):
        get_profile("nope", tmp_store)
