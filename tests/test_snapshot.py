"""Tests for envswitch/snapshot.py"""

import json
import pytest
from pathlib import Path

from envswitch import snapshot as snap


@pytest.fixture(autouse=True)
def tmp_snapshot(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    monkeypatch.setattr("envswitch.storage.get_store_path", lambda: store_file)
    monkeypatch.setattr("envswitch.snapshot.get_store_path", lambda: store_file)
    yield tmp_path


def test_load_snapshots_empty():
    assert snap.load_snapshots() == []


def test_create_snapshot_returns_dict():
    s = snap.create_snapshot("dev", {"KEY": "val"})
    assert s["profile"] == "dev"
    assert s["variables"] == {"KEY": "val"}
    assert "id" in s
    assert "timestamp" in s


def test_create_snapshot_persists():
    snap.create_snapshot("dev", {"A": "1"})
    snap.create_snapshot("prod", {"B": "2"})
    all_snaps = snap.load_snapshots()
    assert len(all_snaps) == 2


def test_list_snapshots_all():
    snap.create_snapshot("dev", {"X": "1"})
    snap.create_snapshot("prod", {"Y": "2"})
    result = snap.list_snapshots()
    assert len(result) == 2


def test_list_snapshots_filtered_by_profile():
    snap.create_snapshot("dev", {"X": "1"})
    snap.create_snapshot("prod", {"Y": "2"})
    snap.create_snapshot("dev", {"X": "3"})
    result = snap.list_snapshots("dev")
    assert len(result) == 2
    assert all(s["profile"] == "dev" for s in result)


def test_get_snapshot_by_id():
    s = snap.create_snapshot("dev", {"K": "v"})
    found = snap.get_snapshot_by_id(s["id"])
    assert found is not None
    assert found["profile"] == "dev"


def test_get_snapshot_by_id_missing():
    assert snap.get_snapshot_by_id(9999999) is None


def test_delete_snapshot_success():
    s = snap.create_snapshot("dev", {"K": "v"})
    result = snap.delete_snapshot(s["id"])
    assert result is True
    assert snap.get_snapshot_by_id(s["id"]) is None


def test_delete_snapshot_not_found():
    result = snap.delete_snapshot(9999999)
    assert result is False


def test_create_snapshot_with_label():
    s = snap.create_snapshot("dev", {"K": "v"}, label="before-deploy")
    assert s["label"] == "before-deploy"
