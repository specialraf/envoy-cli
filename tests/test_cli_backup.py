"""Tests for envoy.cli_backup commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envoy.cli_backup import backup_cmd
from envoy.storage import save_env

PASSWORD = "s3cret"


@pytest.fixture()
def store(tmp_path, monkeypatch):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setattr("envoy.storage._get_store_path", lambda: store_dir)
    return store_dir


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


def test_create_backup_success(store, tmp_path, runner):
    save_env("myproject", {"TOKEN": "abc"}, PASSWORD)
    dest = tmp_path / "bk"

    result = runner.invoke(
        backup_cmd, ["create", "--dest", str(dest), "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_create_backup_no_projects_fails(store, tmp_path, runner):
    result = runner.invoke(
        backup_cmd, ["create", "--dest", str(tmp_path), "--password", PASSWORD]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_restore_backup_success(store, tmp_path, runner):
    save_env("proj", {"K": "v"}, PASSWORD)
    dest = tmp_path / "bk"

    runner.invoke(backup_cmd, ["create", "--dest", str(dest), "--password", PASSWORD])
    archives = list(dest.glob("*.tar"))
    assert archives

    # Remove saved project to allow restore
    for f in store.iterdir():
        f.unlink()

    result = runner.invoke(
        backup_cmd, ["restore", str(archives[0]), "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_restore_nothing_without_overwrite(store, tmp_path, runner):
    save_env("proj", {"K": "v"}, PASSWORD)
    dest = tmp_path / "bk"

    runner.invoke(backup_cmd, ["create", "--dest", str(dest), "--password", PASSWORD])
    archives = list(dest.glob("*.tar"))

    result = runner.invoke(
        backup_cmd, ["restore", str(archives[0]), "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Nothing restored" in result.output


def test_restore_missing_archive_fails(store, tmp_path, runner):
    fake = tmp_path / "nope.tar"
    result = runner.invoke(
        backup_cmd, ["restore", str(fake), "--password", PASSWORD]
    )
    assert result.exit_code != 0
