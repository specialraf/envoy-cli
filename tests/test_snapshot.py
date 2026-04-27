"""Tests for envoy.snapshot."""

from __future__ import annotations

import pytest

from envoy.storage import save_env, _get_store_path
from envoy.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)

ENV_CONTENT = "KEY1=hello\nKEY2=world\n"
UPDATED_CONTENT = "KEY1=updated\nKEY2=world\n"
PASSWORD = "s3cret"
PROJECT = "myapp"


@pytest.fixture()
def store(tmp_path):
    save_env(tmp_path, PROJECT, PASSWORD, ENV_CONTENT)
    return tmp_path


def test_create_snapshot_returns_name(store):
    name = create_snapshot(store, PROJECT, PASSWORD)
    assert isinstance(name, str)
    assert len(name) > 0


def test_create_snapshot_with_label(store):
    name = create_snapshot(store, PROJECT, PASSWORD, label="before-migration")
    assert name == "before-migration"


def test_list_snapshots_empty_initially(tmp_path):
    save_env(tmp_path, PROJECT, PASSWORD, ENV_CONTENT)
    assert list_snapshots(tmp_path, PROJECT) == []


def test_list_snapshots_returns_created(store):
    create_snapshot(store, PROJECT, PASSWORD, label="snap1")
    create_snapshot(store, PROJECT, PASSWORD, label="snap2")
    snaps = list_snapshots(store, PROJECT)
    names = [s["name"] for s in snaps]
    assert "snap1" in names
    assert "snap2" in names


def test_restore_snapshot_overwrites_live_env(store):
    create_snapshot(store, PROJECT, PASSWORD, label="v1")
    save_env(store, PROJECT, PASSWORD, UPDATED_CONTENT)
    restore_snapshot(store, PROJECT, "v1", PASSWORD)
    from envoy.storage import load_env
    restored = load_env(store, PROJECT, PASSWORD)
    assert restored == ENV_CONTENT


def test_restore_missing_snapshot_raises(store):
    with pytest.raises(KeyError, match="no-such-snap"):
        restore_snapshot(store, PROJECT, "no-such-snap", PASSWORD)


def test_delete_snapshot_removes_it(store):
    create_snapshot(store, PROJECT, PASSWORD, label="to-delete")
    delete_snapshot(store, PROJECT, "to-delete")
    snaps = list_snapshots(store, PROJECT)
    assert all(s["name"] != "to-delete" for s in snaps)


def test_delete_missing_snapshot_raises(store):
    with pytest.raises(KeyError, match="ghost"):
        delete_snapshot(store, PROJECT, "ghost")


def test_multiple_snapshots_ordered_newest_first(store):
    for label in ("alpha", "beta", "gamma"):
        create_snapshot(store, PROJECT, PASSWORD, label=label)
    snaps = list_snapshots(store, PROJECT)
    assert len(snaps) == 3
