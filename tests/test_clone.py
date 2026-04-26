"""Tests for envswitch.clone module."""

import pytest
from envswitch.clone import clone_profile, CloneError
from envswitch.storage import load_profiles, save_profiles


@pytest.fixture
def tmp_store(tmp_path):
    store = tmp_path / "profiles.json"
    profiles = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "staging": {"DB_HOST": "staging.db", "DB_PORT": "5432", "DEBUG": "false"},
    }
    save_profiles(profiles, store_path=str(store))
    return str(store)


def test_clone_creates_new_profile(tmp_store):
    clone_profile("dev", "dev-copy", store_path=tmp_store)
    profiles = load_profiles(store_path=tmp_store)
    assert "dev-copy" in profiles


def test_clone_copies_all_keys(tmp_store):
    clone_profile("dev", "dev-copy", store_path=tmp_store)
    profiles = load_profiles(store_path=tmp_store)
    assert profiles["dev-copy"] == profiles["dev"]


def test_clone_does_not_mutate_source(tmp_store):
    clone_profile("dev", "dev-copy", overrides={"DEBUG": "false"}, store_path=tmp_store)
    profiles = load_profiles(store_path=tmp_store)
    assert profiles["dev"]["DEBUG"] == "true"


def test_clone_applies_overrides(tmp_store):
    clone_profile(
        "dev",
        "dev-local",
        overrides={"DB_HOST": "myhost", "NEW_KEY": "value"},
        store_path=tmp_store,
    )
    profiles = load_profiles(store_path=tmp_store)
    assert profiles["dev-local"]["DB_HOST"] == "myhost"
    assert profiles["dev-local"]["NEW_KEY"] == "value"
    assert profiles["dev-local"]["DB_PORT"] == "5432"


def test_clone_preserves_other_profiles(tmp_store):
    clone_profile("dev", "dev-copy", store_path=tmp_store)
    profiles = load_profiles(store_path=tmp_store)
    assert "staging" in profiles
    assert profiles["staging"]["DB_HOST"] == "staging.db"


def test_clone_nonexistent_source_raises(tmp_store):
    with pytest.raises(CloneError) as exc_info:
        clone_profile("nonexistent", "new-profile", store_path=tmp_store)
    assert "nonexistent" in exc_info.value.message


def test_clone_existing_destination_raises(tmp_store):
    with pytest.raises(CloneError) as exc_info:
        clone_profile("dev", "staging", store_path=tmp_store)
    assert "staging" in exc_info.value.message


def test_clone_returns_cloned_dict(tmp_store):
    result = clone_profile("dev", "dev-copy", store_path=tmp_store)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
