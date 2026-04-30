"""Tests for envswitch.group"""

import pytest
from pathlib import Path

from envswitch.group import (
    add_profile_to_group,
    remove_profile_from_group,
    list_groups,
    get_group_members,
    get_groups_for_profile,
    GroupError,
)
from envswitch.storage import save_profiles


@pytest.fixture
def tmp_store(tmp_path):
    profiles = {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        "staging": {"DB_HOST": "staging.db", "DEBUG": "false"},
        "prod": {"DB_HOST": "prod.db", "DEBUG": "false"},
    }
    save_profiles(tmp_path, profiles)
    return tmp_path


def test_add_profile_to_group(tmp_store):
    add_profile_to_group(tmp_store, "backend", "dev")
    members = get_group_members(tmp_store, "backend")
    assert "dev" in members


def test_add_multiple_profiles_to_group(tmp_store):
    add_profile_to_group(tmp_store, "backend", "dev")
    add_profile_to_group(tmp_store, "backend", "staging")
    members = get_group_members(tmp_store, "backend")
    assert set(members) == {"dev", "staging"}


def test_add_duplicate_raises(tmp_store):
    add_profile_to_group(tmp_store, "backend", "dev")
    with pytest.raises(GroupError, match="already in group"):
        add_profile_to_group(tmp_store, "backend", "dev")


def test_add_nonexistent_profile_raises(tmp_store):
    with pytest.raises(GroupError, match="does not exist"):
        add_profile_to_group(tmp_store, "backend", "ghost")


def test_remove_profile_from_group(tmp_store):
    add_profile_to_group(tmp_store, "backend", "dev")
    remove_profile_from_group(tmp_store, "backend", "dev")
    groups = list_groups(tmp_store)
    assert "backend" not in groups


def test_remove_profile_not_in_group_raises(tmp_store):
    with pytest.raises(GroupError, match="not in group"):
        remove_profile_from_group(tmp_store, "backend", "dev")


def test_list_groups_empty(tmp_store):
    assert list_groups(tmp_store) == {}


def test_list_groups_multiple(tmp_store):
    add_profile_to_group(tmp_store, "backend", "dev")
    add_profile_to_group(tmp_store, "cloud", "prod")
    groups = list_groups(tmp_store)
    assert "backend" in groups
    assert "cloud" in groups


def test_get_group_members_unknown_group_raises(tmp_store):
    with pytest.raises(GroupError, match="does not exist"):
        get_group_members(tmp_store, "nope")


def test_get_groups_for_profile(tmp_store):
    add_profile_to_group(tmp_store, "backend", "dev")
    add_profile_to_group(tmp_store, "all", "dev")
    result = get_groups_for_profile(tmp_store, "dev")
    assert set(result) == {"backend", "all"}


def test_get_groups_for_profile_none(tmp_store):
    result = get_groups_for_profile(tmp_store, "dev")
    assert result == []


def test_group_persists_across_calls(tmp_store):
    add_profile_to_group(tmp_store, "team", "staging")
    # reload from disk
    members = get_group_members(tmp_store, "team")
    assert "staging" in members
