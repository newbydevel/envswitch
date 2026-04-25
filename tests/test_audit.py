"""Tests for envswitch/audit.py"""

import pytest
from pathlib import Path
from envswitch.audit import (
    get_audit_path,
    load_audit,
    save_audit,
    record_event,
    get_events_for_profile,
    clear_audit,
)


@pytest.fixture
def audit_file(tmp_path):
    return get_audit_path(base_dir=tmp_path)


def test_load_audit_empty(audit_file):
    entries = load_audit(audit_file)
    assert entries == []


def test_save_and_load_audit(audit_file):
    entries = [{"timestamp": "2024-01-01T00:00:00+00:00", "action": "apply", "profile": "dev"}]
    save_audit(audit_file, entries)
    loaded = load_audit(audit_file)
    assert loaded == entries


def test_record_event_creates_entry(audit_file):
    entry = record_event(audit_file, "apply", "dev")
    assert entry["action"] == "apply"
    assert entry["profile"] == "dev"
    assert "timestamp" in entry


def test_record_event_appends(audit_file):
    record_event(audit_file, "apply", "dev")
    record_event(audit_file, "delete", "staging")
    entries = load_audit(audit_file)
    assert len(entries) == 2
    assert entries[0]["action"] == "apply"
    assert entries[1]["action"] == "delete"


def test_record_event_with_details(audit_file):
    entry = record_event(audit_file, "rename", "dev", details={"new_name": "dev2"})
    assert entry["details"] == {"new_name": "dev2"}
    loaded = load_audit(audit_file)
    assert loaded[0]["details"] == {"new_name": "dev2"}


def test_get_events_for_profile(audit_file):
    record_event(audit_file, "apply", "dev")
    record_event(audit_file, "apply", "prod")
    record_event(audit_file, "delete", "dev")
    dev_events = get_events_for_profile(audit_file, "dev")
    assert len(dev_events) == 2
    assert all(e["profile"] == "dev" for e in dev_events)


def test_get_events_for_profile_none_found(audit_file):
    record_event(audit_file, "apply", "dev")
    events = get_events_for_profile(audit_file, "staging")
    assert events == []


def test_clear_audit(audit_file):
    record_event(audit_file, "apply", "dev")
    record_event(audit_file, "apply", "prod")
    clear_audit(audit_file)
    assert load_audit(audit_file) == []
