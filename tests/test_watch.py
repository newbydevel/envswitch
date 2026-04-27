"""Tests for envswitch/watch.py"""

import pytest
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from envswitch.watch import (
    WatchError,
    get_mtime,
    watch_file,
    make_reload_callback,
)


def test_get_mtime_returns_float(tmp_path):
    f = tmp_path / "test.env"
    f.write_text("KEY=val")
    result = get_mtime(f)
    assert isinstance(result, float)


def test_get_mtime_returns_none_for_missing_file(tmp_path):
    result = get_mtime(tmp_path / "nonexistent.env")
    assert result is None


def test_watch_file_raises_if_file_missing(tmp_path):
    with pytest.raises(WatchError, match="File not found"):
        watch_file(tmp_path / "missing.env", callback=lambda p: None, max_iterations=1)


def test_watch_file_calls_callback_on_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=original")

    callback = MagicMock()
    call_count = [0]

    original_sleep = time.sleep

    def fake_sleep(n):
        # On first iteration, modify the file to simulate a change
        if call_count[0] == 0:
            time.sleep(0.01)  # tiny real sleep
            env_file.write_text("KEY=changed")
            # bump mtime manually to ensure it differs
            new_time = env_file.stat().st_mtime + 1
            import os
            os.utime(env_file, (new_time, new_time))
        call_count[0] += 1

    with patch("envswitch.watch.time.sleep", side_effect=fake_sleep):
        watch_file(env_file, callback=callback, interval=0.01, max_iterations=2)

    assert callback.called
    assert callback.call_args[0][0] == env_file


def test_watch_file_no_callback_if_no_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=stable")

    callback = MagicMock()

    with patch("envswitch.watch.time.sleep"):
        watch_file(env_file, callback=callback, interval=0.01, max_iterations=3)

    callback.assert_not_called()


def test_watch_file_raises_if_file_disappears(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")

    call_count = [0]

    def fake_sleep(n):
        if call_count[0] == 0:
            env_file.unlink()
        call_count[0] += 1

    with patch("envswitch.watch.time.sleep", side_effect=fake_sleep):
        with pytest.raises(WatchError, match="disappeared"):
            watch_file(env_file, callback=MagicMock(), interval=0.01, max_iterations=3)


def test_make_reload_callback_invokes_apply(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")

    apply_fn = MagicMock()
    target = tmp_path / "output.env"
    cb = make_reload_callback("myprofile", apply_fn, target)

    cb(env_file)

    apply_fn.assert_called_once_with("myprofile", target)
