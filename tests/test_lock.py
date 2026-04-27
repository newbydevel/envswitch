import pytest
from pathlib import Path
from envswitch.lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    list_locked,
    assert_not_locked,
    LockError,
)


@pytest.fixture
def lock_file(tmp_path):
    return tmp_path / "locks.json"


def test_lock_profile_creates_entry(lock_file):
    lock_profile("prod", lock_file)
    assert is_locked("prod", lock_file)


def test_lock_profile_duplicate_raises(lock_file):
    lock_profile("prod", lock_file)
    with pytest.raises(LockError, match="already locked"):
        lock_profile("prod", lock_file)


def test_unlock_profile_removes_entry(lock_file):
    lock_profile("prod", lock_file)
    unlock_profile("prod", lock_file)
    assert not is_locked("prod", lock_file)


def test_unlock_not_locked_raises(lock_file):
    with pytest.raises(LockError, match="not locked"):
        unlock_profile("staging", lock_file)


def test_is_locked_returns_false_when_missing(lock_file):
    assert not is_locked("dev", lock_file)


def test_list_locked_empty(lock_file):
    assert list_locked(lock_file) == []


def test_list_locked_multiple(lock_file):
    lock_profile("prod", lock_file)
    lock_profile("staging", lock_file)
    locked = list_locked(lock_file)
    assert "prod" in locked
    assert "staging" in locked
    assert len(locked) == 2


def test_assert_not_locked_passes_when_unlocked(lock_file):
    # should not raise
    assert_not_locked("dev", lock_file)


def test_assert_not_locked_raises_when_locked(lock_file):
    lock_profile("prod", lock_file)
    with pytest.raises(LockError, match="locked and cannot be modified"):
        assert_not_locked("prod", lock_file)


def test_lock_persists_across_calls(lock_file):
    lock_profile("prod", lock_file)
    # reload from disk
    assert is_locked("prod", lock_file)
    assert not is_locked("dev", lock_file)


def test_unlock_only_removes_target(lock_file):
    lock_profile("prod", lock_file)
    lock_profile("staging", lock_file)
    unlock_profile("prod", lock_file)
    assert not is_locked("prod", lock_file)
    assert is_locked("staging", lock_file)
