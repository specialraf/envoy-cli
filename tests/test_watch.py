"""Tests for envoy.watch."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envoy.watch import _file_hash, watch_file
from envoy.storage import save_env, load_env


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / "store"))
    return tmp_path


def test_file_hash_is_stable(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value")
    assert _file_hash(f) == _file_hash(f)


def test_file_hash_changes_on_edit(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value")
    h1 = _file_hash(f)
    f.write_text("KEY=changed")
    h2 = _file_hash(f)
    assert h1 != h2


def test_watch_file_raises_if_missing(store):
    with pytest.raises(FileNotFoundError):
        watch_file("/no/such/file.env", "proj", "pass", max_iterations=1)


def test_watch_file_no_change_does_not_save(store, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")

    with patch("envoy.watch.save_env") as mock_save:
        watch_file(
            path=str(env_file),
            project="myproj",
            password="secret",
            interval=0,
            max_iterations=2,
        )
    mock_save.assert_not_called()


def test_watch_file_detects_change_and_saves(store, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=original")

    call_count = 0

    def fake_sleep(interval):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            env_file.write_text("KEY=updated")

    with patch("envoy.watch.time.sleep", side_effect=fake_sleep), \
         patch("envoy.watch.save_env") as mock_save, \
         patch("envoy.watch.record"):
        watch_file(
            path=str(env_file),
            project="myproj",
            password="secret",
            interval=0,
            max_iterations=2,
        )

    mock_save.assert_called_once_with("myproj", "KEY=updated", "secret")


def test_watch_file_calls_on_change_callback(store, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")
    received = []

    def fake_sleep(interval):
        env_file.write_text("A=2")

    with patch("envoy.watch.time.sleep", side_effect=fake_sleep), \
         patch("envoy.watch.save_env"), \
         patch("envoy.watch.record"):
        watch_file(
            path=str(env_file),
            project="proj",
            password="pw",
            interval=0,
            on_change=received.append,
            max_iterations=1,
        )

    assert received == ["A=2"]
