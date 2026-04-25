"""Tests for envswitch.rename module."""

import pytest
from envswitch.rename import rename_profile, copy_profile, RenameError
from envswitch.storage import load_profiles, save_profiles


@pytest.fixture
def tmp_store(tmp_path):
    store = tmp_path / "profiles.json"
    save_profiles(str(store), {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        "prod": {"DB_HOST": "prod.db.internal", "DEBUG": "false"},
    })
    return str(store)


def test_rename_profile_success(tmp_store):
    rename_profile(tmp_store, "dev", "development")
    profiles = load_profiles(tmp_store)
    assert "development" in profiles
    assert "dev" not in profiles
    assert profiles["development"]["DB_HOST"] == "localhost"


def test_rename_preserves_other_profiles(tmp_store):
    rename_profile(tmp_store, "dev", "staging")
    profiles = load_profiles(tmp_store)
    assert "prod" in profiles
    assert "staging" in profiles


def test_rename_nonexistent_raises(tmp_store):
    with pytest.raises(RenameError, match="does not exist"):
        rename_profile(tmp_store, "ghost", "newname")


def test_rename_to_existing_raises(tmp_store):
    with pytest.raises(RenameError, match="already exists"):
        rename_profile(tmp_store, "dev", "prod")


def test_rename_to_empty_name_raises(tmp_store):
    with pytest.raises(RenameError, match="cannot be empty"):
        rename_profile(tmp_store, "dev", "")


def test_copy_profile_success(tmp_store):
    copy_profile(tmp_store, "dev", "dev-copy")
    profiles = load_profiles(tmp_store)
    assert "dev-copy" in profiles
    assert "dev" in profiles
    assert profiles["dev-copy"] == profiles["dev"]


def test_copy_is_independent(tmp_store):
    copy_profile(tmp_store, "dev", "dev-copy")
    profiles = load_profiles(tmp_store)
    profiles["dev-copy"]["DB_HOST"] = "changed"
    assert profiles["dev"]["DB_HOST"] == "localhost"


def test_copy_nonexistent_raises(tmp_store):
    with pytest.raises(RenameError, match="does not exist"):
        copy_profile(tmp_store, "ghost", "newname")


def test_copy_to_existing_raises(tmp_store):
    with pytest.raises(RenameError, match="already exists"):
        copy_profile(tmp_store, "dev", "prod")


def test_copy_to_empty_name_raises(tmp_store):
    with pytest.raises(RenameError, match="cannot be empty"):
        copy_profile(tmp_store, "dev", "  ")
