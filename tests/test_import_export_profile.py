"""Tests for envswitch.import_export_profile."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envswitch.import_export_profile import (
    export_profile_to_file,
    import_profile_from_file,
    ImportExportError,
)


SAMPLE_PROFILES = {
    "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
    "prod": {"DB_HOST": "prod.db.internal", "DEBUG": "false"},
}


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    monkeypatch.setattr("envswitch.storage.get_store_path", lambda: store_file)
    return store_file


def test_export_dotenv_creates_file(tmp_store, tmp_path):
    from envswitch.storage import save_profiles
    save_profiles(SAMPLE_PROFILES)
    out = tmp_path / "dev.env"
    export_profile_to_file("dev", str(out), fmt="dotenv")
    assert out.exists()
    content = out.read_text()
    assert "DB_HOST=localhost" in content
    assert "DEBUG=true" in content


def test_export_json_creates_file(tmp_store, tmp_path):
    from envswitch.storage import save_profiles
    save_profiles(SAMPLE_PROFILES)
    out = tmp_path / "dev.json"
    export_profile_to_file("dev", str(out), fmt="json")
    data = json.loads(out.read_text())
    assert data == {"DB_HOST": "localhost", "DEBUG": "true"}


def test_export_unknown_format_raises(tmp_store):
    from envswitch.storage import save_profiles
    save_profiles(SAMPLE_PROFILES)
    with pytest.raises(ImportExportError, match="Unsupported format"):
        export_profile_to_file("dev", "/tmp/x.xml", fmt="xml")


def test_export_missing_profile_raises(tmp_store):
    from envswitch.storage import save_profiles
    save_profiles({})
    with pytest.raises(ImportExportError, match="not found"):
        export_profile_to_file("ghost", "/tmp/ghost.env")


def test_import_dotenv_file(tmp_store, tmp_path):
    env_file = tmp_path / "staging.env"
    env_file.write_text("API_URL=https://staging.example.com\nTIMEOUT=30\n")
    import_profile_from_file("staging", str(env_file), fmt="dotenv")
    from envswitch.storage import load_profiles
    profiles = load_profiles()
    assert profiles["staging"]["API_URL"] == "https://staging.example.com"
    assert profiles["staging"]["TIMEOUT"] == "30"


def test_import_json_file(tmp_store, tmp_path):
    json_file = tmp_path / "ci.json"
    json_file.write_text(json.dumps({"CI": "true", "BUILD_NUM": "42"}))
    import_profile_from_file("ci", str(json_file), fmt="json")
    from envswitch.storage import load_profiles
    profiles = load_profiles()
    assert profiles["ci"]["CI"] == "true"


def test_import_duplicate_raises_without_overwrite(tmp_store, tmp_path):
    from envswitch.storage import save_profiles
    save_profiles({"dev": {"X": "1"}})
    env_file = tmp_path / "dev.env"
    env_file.write_text("X=2\n")
    with pytest.raises(ImportExportError, match="already exists"):
        import_profile_from_file("dev", str(env_file))


def test_import_overwrite_replaces_profile(tmp_store, tmp_path):
    from envswitch.storage import save_profiles, load_profiles
    save_profiles({"dev": {"X": "1"}})
    env_file = tmp_path / "dev.env"
    env_file.write_text("X=99\n")
    import_profile_from_file("dev", str(env_file), overwrite=True)
    assert load_profiles()["dev"]["X"] == "99"


def test_import_missing_file_raises(tmp_store):
    with pytest.raises(ImportExportError, match="File not found"):
        import_profile_from_file("new", "/nonexistent/path.env")


def test_import_invalid_json_raises(tmp_store, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json at all")
    with pytest.raises(ImportExportError, match="Invalid JSON"):
        import_profile_from_file("bad", str(bad), fmt="json")
