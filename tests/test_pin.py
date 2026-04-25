"""Tests for envswitch.pin module."""

import json
import pytest
from pathlib import Path
from envswitch.pin import (
    pin_profile,
    unpin_profile,
    read_pin,
    resolve_pin,
    PinError,
    PIN_FILENAME,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_pin_creates_file(tmp_dir):
    pin_file = pin_profile("production", tmp_dir)
    assert pin_file.exists()
    assert pin_file.name == PIN_FILENAME


def test_pin_stores_profile_name(tmp_dir):
    pin_profile("staging", tmp_dir)
    data = json.loads((Path(tmp_dir) / PIN_FILENAME).read_text())
    assert data["profile"] == "staging"


def test_read_pin_returns_profile(tmp_dir):
    pin_profile("dev", tmp_dir)
    assert read_pin(tmp_dir) == "dev"


def test_read_pin_returns_none_if_no_file(tmp_dir):
    assert read_pin(tmp_dir) is None


def test_read_pin_raises_on_malformed_file(tmp_dir):
    (Path(tmp_dir) / PIN_FILENAME).write_text("not json")
    with pytest.raises(PinError, match="Malformed pin file"):
        read_pin(tmp_dir)


def test_unpin_removes_file(tmp_dir):
    pin_profile("dev", tmp_dir)
    unpin_profile(tmp_dir)
    assert not (Path(tmp_dir) / PIN_FILENAME).exists()


def test_unpin_raises_if_no_pin(tmp_dir):
    with pytest.raises(PinError, match="No pin file found"):
        unpin_profile(tmp_dir)


def test_pin_overwrites_existing(tmp_dir):
    pin_profile("dev", tmp_dir)
    pin_profile("prod", tmp_dir)
    assert read_pin(tmp_dir) == "prod"


def test_resolve_pin_finds_in_subdir(tmp_path):
    pin_profile("base-env", str(tmp_path))
    subdir = tmp_path / "a" / "b"
    subdir.mkdir(parents=True)
    result = resolve_pin(str(subdir))
    assert result == "base-env"


def test_resolve_pin_returns_none_if_not_found(tmp_path):
    subdir = tmp_path / "x"
    subdir.mkdir()
    assert resolve_pin(str(subdir)) is None


def test_resolve_pin_prefers_nearest(tmp_path):
    pin_profile("outer", str(tmp_path))
    inner = tmp_path / "inner"
    inner.mkdir()
    pin_profile("inner-env", str(inner))
    assert resolve_pin(str(inner)) == "inner-env"
