import pytest
from envswitch.diff import diff_profiles, format_diff


@pytest.fixture
def base():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


@pytest.fixture
def updated():
    return {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "info"}


def test_diff_added(base, updated):
    added, removed, changed = diff_profiles(base, updated)
    assert ("LOG_LEVEL", "info") in added


def test_diff_removed(base, updated):
    added, removed, changed = diff_profiles(base, updated)
    assert ("DEBUG", "true") in removed


def test_diff_changed(base, updated):
    added, removed, changed = diff_profiles(base, updated)
    assert ("HOST", "localhost", "prod.example.com") in changed


def test_diff_unchanged_key_not_in_changed(base, updated):
    added, removed, changed = diff_profiles(base, updated)
    changed_keys = [k for k, _, _ in changed]
    assert "PORT" not in changed_keys


def test_diff_identical_profiles():
    env = {"A": "1", "B": "2"}
    added, removed, changed = diff_profiles(env, env)
    assert added == []
    assert removed == []
    assert changed == []


def test_diff_empty_old():
    added, removed, changed = diff_profiles({}, {"X": "y"})
    assert added == [("X", "y")]
    assert removed == []
    assert changed == []


def test_diff_empty_new():
    added, removed, changed = diff_profiles({"X": "y"}, {})
    assert added == []
    assert removed == [("X", "y")]
    assert changed == []


def test_format_diff_no_color():
    added = [("NEW_KEY", "val")]
    removed = [("OLD_KEY", "old")]
    changed = [("HOST", "localhost", "remote")]
    output = format_diff(added, removed, changed, use_color=False)
    assert "+ NEW_KEY=val" in output
    assert "- OLD_KEY=old" in output
    assert "~ HOST" in output
    assert "localhost" in output
    assert "remote" in output


def test_format_diff_no_differences():
    output = format_diff([], [], [], use_color=False)
    assert output == "No differences."


def test_format_diff_sorted_keys():
    added = [("Z_KEY", "1"), ("A_KEY", "2")]
    output = format_diff(added, [], [], use_color=False)
    lines = output.strip().splitlines()
    assert lines[0].startswith("+ A_KEY") or lines[1].startswith("+ A_KEY")
