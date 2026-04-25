"""Tests for envswitch/cli_snapshot.py"""

import pytest
from click.testing import CliRunner
from envswitch.cli_snapshot import cmd_snapshot
from envswitch import snapshot as snap
from envswitch.storage import save_profiles


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def patch_paths(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envswitch.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envswitch.snapshot.get_store_path", lambda: store)
    monkeypatch.setattr("envswitch.cli_snapshot.snap.get_store_path", lambda: store, raising=False)
    yield


def invoke(runner, *args):
    return runner.invoke(cmd_snapshot, list(args))


def test_save_snapshot(runner):
    save_profiles({"dev": {"KEY": "value"}})
    result = invoke(runner, "save", "dev")
    assert result.exit_code == 0
    assert "Snapshot saved" in result.output


def test_save_snapshot_with_label(runner):
    save_profiles({"dev": {"KEY": "value"}})
    result = invoke(runner, "save", "dev", "--label", "pre-release")
    assert result.exit_code == 0
    assert "pre-release" in result.output


def test_save_snapshot_unknown_profile(runner):
    save_profiles({})
    result = invoke(runner, "save", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_list_snapshots_empty(runner):
    result = invoke(runner, "list")
    assert result.exit_code == 0
    assert "No snapshots found" in result.output


def test_list_snapshots_shows_entries(runner):
    save_profiles({"dev": {"A": "1"}})
    invoke(runner, "save", "dev")
    result = invoke(runner, "list")
    assert "dev" in result.output


def test_list_snapshots_filtered(runner):
    save_profiles({"dev": {"A": "1"}, "prod": {"B": "2"}})
    invoke(runner, "save", "dev")
    invoke(runner, "save", "prod")
    result = invoke(runner, "list", "dev")
    assert "dev" in result.output
    assert "prod" not in result.output


def test_show_snapshot(runner):
    save_profiles({"dev": {"MYVAR": "hello"}})
    invoke(runner, "save", "dev")
    snapshots = snap.list_snapshots()
    sid = snapshots[0]["id"]
    result = invoke(runner, "show", str(sid))
    assert "MYVAR" in result.output
    assert "hello" in result.output


def test_show_snapshot_not_found(runner):
    result = invoke(runner, "show", "9999999")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_delete_snapshot(runner):
    save_profiles({"dev": {"X": "1"}})
    invoke(runner, "save", "dev")
    sid = snap.list_snapshots()[0]["id"]
    result = invoke(runner, "delete", str(sid))
    assert result.exit_code == 0
    assert "deleted" in result.output
    assert snap.get_snapshot_by_id(sid) is None


def test_delete_snapshot_not_found(runner):
    result = invoke(runner, "delete", "9999999")
    assert result.exit_code != 0
