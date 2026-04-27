"""Tests for envoy.cli_snapshot."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.storage import save_env
from envoy.snapshot import create_snapshot
from envoy.cli_snapshot import snapshot_cmd

ENV_CONTENT = "KEY=value\n"
PASSWORD = "pass"
PROJECT = "testapp"


@pytest.fixture()
def store(tmp_path):
    save_env(tmp_path, PROJECT, PASSWORD, ENV_CONTENT)
    return tmp_path


@pytest.fixture()
def runner(store, monkeypatch):
    monkeypatch.setattr("envoy.cli_snapshot._get_store_path", lambda: store)
    monkeypatch.setattr("envoy.cli_snapshot._prompt_password", lambda **_: PASSWORD)
    return CliRunner()


def test_create_snapshot_success(runner):
    result = runner.invoke(snapshot_cmd, ["create", PROJECT, "--label", "v1"])
    assert result.exit_code == 0
    assert "v1" in result.output


def test_create_snapshot_no_label(runner):
    result = runner.invoke(snapshot_cmd, ["create", PROJECT])
    assert result.exit_code == 0
    assert "Snapshot created" in result.output


def test_list_snapshots_empty(runner, store):
    result = runner.invoke(snapshot_cmd, ["list", PROJECT])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_list_snapshots_shows_label(runner, store):
    create_snapshot(store, PROJECT, PASSWORD, label="my-snap")
    result = runner.invoke(snapshot_cmd, ["list", PROJECT])
    assert result.exit_code == 0
    assert "my-snap" in result.output


def test_restore_snapshot_success(runner, store):
    create_snapshot(store, PROJECT, PASSWORD, label="snap1")
    result = runner.invoke(snapshot_cmd, ["restore", PROJECT, "snap1"])
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_restore_missing_snapshot_fails(runner):
    result = runner.invoke(snapshot_cmd, ["restore", PROJECT, "ghost"])
    assert result.exit_code != 0
    assert "ghost" in result.output


def test_delete_snapshot_success(runner, store):
    create_snapshot(store, PROJECT, PASSWORD, label="old")
    result = runner.invoke(snapshot_cmd, ["delete", PROJECT, "old"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_delete_missing_snapshot_fails(runner):
    result = runner.invoke(snapshot_cmd, ["delete", PROJECT, "nope"])
    assert result.exit_code != 0
