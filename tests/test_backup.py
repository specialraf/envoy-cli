"""Tests for envoy.backup module."""

from __future__ import annotations

import json
import tarfile
from pathlib import Path

import pytest

from envoy.backup import backup_all, restore_all
from envoy.storage import save_env, load_env, list_projects

PASSWORD = "s3cret"


@pytest.fixture()
def store(tmp_path, monkeypatch):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setattr("envoy.storage._get_store_path", lambda: store_dir)
    return store_dir


def test_backup_all_creates_archive(store, tmp_path):
    save_env("alpha", {"KEY": "val1"}, PASSWORD)
    save_env("beta", {"KEY": "val2"}, PASSWORD)

    dest = tmp_path / "backups"
    archive = backup_all(PASSWORD, dest)

    assert archive.exists()
    assert archive.suffix == ".tar"


def test_backup_archive_contains_all_projects(store, tmp_path):
    save_env("proj1", {"A": "1"}, PASSWORD)
    save_env("proj2", {"B": "2"}, PASSWORD)

    archive = backup_all(PASSWORD, tmp_path / "bk")

    with tarfile.open(archive, "r") as tar:
        names = {m.name for m in tar.getmembers()}
    assert "proj1.json" in names
    assert "proj2.json" in names


def test_backup_no_projects_raises(store, tmp_path):
    with pytest.raises(ValueError, match="No projects"):
        backup_all(PASSWORD, tmp_path / "bk")


def test_backup_creates_dest_directory_if_missing(store, tmp_path):
    """backup_all should create the destination directory when it doesn't exist."""
    save_env("alpha", {"KEY": "val"}, PASSWORD)

    dest = tmp_path / "nested" / "backups"
    assert not dest.exists()

    archive = backup_all(PASSWORD, dest)

    assert dest.exists()
    assert archive.exists()


def test_restore_all_loads_projects(store, tmp_path):
    save_env("gamma", {"X": "10"}, PASSWORD)
    archive = backup_all(PASSWORD, tmp_path / "bk")

    # wipe store
    for f in store.iterdir():
        f.unlink()

    restored = restore_all(PASSWORD, archive)
    assert "gamma" in restored
    assert load_env("gamma", PASSWORD) == {"X": "10"}


def test_restore_skips_existing_without_overwrite(store, tmp_path):
    save_env("delta", {"Y": "old"}, PASSWORD)
    archive = backup_all(PASSWORD, tmp_path / "bk")

    restored = restore_all(PASSWORD, archive, overwrite=False)
    assert restored == []


def test_restore_overwrites_when_flag_set(store, tmp_path):
    save_env("delta", {"Y": "old"}, PASSWORD)
    archive = backup_all(PASSWORD, tmp_path / "bk")
    save_env("delta", {"Y": "new"}, PASSWORD)

    restored = restore_all(PASSWORD, archive, overwrite=True)
    assert "delta" in restored
    assert load_env("delta", PASSWORD) == {"Y": "old"}


def test_restore_missing_archive_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_all(PASSWORD, tmp_path / "nonexistent.tar")
