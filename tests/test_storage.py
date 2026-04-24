"""Tests for envoy.storage."""

import pytest
from pathlib import Path

from envoy.storage import save_env, load_env, list_projects, delete_env

PASSWORD = "hunter2"
PROJECT = "my-app"
ENV_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


@pytest.fixture()
def store(tmp_path):
    """Return a temporary store directory."""
    return tmp_path / "envoy_store"


def test_save_and_load_roundtrip(store):
    save_env(PROJECT, ENV_CONTENT, PASSWORD, store_dir=store)
    result = load_env(PROJECT, PASSWORD, store_dir=store)
    assert result == ENV_CONTENT


def test_load_missing_project_raises(store):
    with pytest.raises(KeyError, match="no-such-project"):
        load_env("no-such-project", PASSWORD, store_dir=store)


def test_wrong_password_raises(store):
    save_env(PROJECT, ENV_CONTENT, PASSWORD, store_dir=store)
    with pytest.raises(Exception):
        load_env(PROJECT, "wrongpassword", store_dir=store)


def test_list_projects_empty(store):
    assert list_projects(store_dir=store) == []


def test_list_projects_returns_sorted(store):
    for name in ("zebra", "alpha", "mango"):
        save_env(name, ENV_CONTENT, PASSWORD, store_dir=store)
    assert list_projects(store_dir=store) == ["alpha", "mango", "zebra"]


def test_overwrite_project(store):
    save_env(PROJECT, ENV_CONTENT, PASSWORD, store_dir=store)
    new_content = "API_KEY=newkey\n"
    save_env(PROJECT, new_content, PASSWORD, store_dir=store)
    result = load_env(PROJECT, PASSWORD, store_dir=store)
    assert result == new_content


def test_delete_env(store):
    save_env(PROJECT, ENV_CONTENT, PASSWORD, store_dir=store)
    delete_env(PROJECT, store_dir=store)
    assert PROJECT not in list_projects(store_dir=store)


def test_delete_missing_project_raises(store):
    with pytest.raises(KeyError, match="ghost"):
        delete_env("ghost", store_dir=store)


def test_store_file_created(store):
    save_env(PROJECT, ENV_CONTENT, PASSWORD, store_dir=store)
    assert (store / "store.json").exists()
