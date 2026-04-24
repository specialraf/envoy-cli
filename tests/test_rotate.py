"""Tests for envoy.rotate (key rotation)."""

from __future__ import annotations

import pytest

from envoy.storage import save_env, load_env, list_projects
from envoy.rotate import rotate_project, rotate_all


OLD_PASS = "old-secret"
NEW_PASS = "new-secret"
SAMPLE_ENV = "API_KEY=abc123\nDEBUG=true\n"


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Redirect storage to a temp directory."""
    monkeypatch.setenv("ENVOY_STORE_PATH", str(tmp_path / "store.json"))
    return tmp_path


def test_rotate_project_allows_load_with_new_password(store):
    save_env("myapp", SAMPLE_ENV, OLD_PASS)
    rotate_project("myapp", OLD_PASS, NEW_PASS)
    result = load_env("myapp", NEW_PASS)
    assert result == SAMPLE_ENV


def test_rotate_project_old_password_fails_after_rotation(store):
    save_env("myapp", SAMPLE_ENV, OLD_PASS)
    rotate_project("myapp", OLD_PASS, NEW_PASS)
    with pytest.raises(Exception):
        load_env("myapp", OLD_PASS)


def test_rotate_project_missing_raises_key_error(store):
    with pytest.raises(KeyError):
        rotate_project("ghost", OLD_PASS, NEW_PASS)


def test_rotate_project_wrong_old_password_raises(store):
    save_env("myapp", SAMPLE_ENV, OLD_PASS)
    with pytest.raises(Exception):
        rotate_project("myapp", "wrong-pass", NEW_PASS)


def test_rotate_all_rotates_every_project(store):
    for name in ("alpha", "beta", "gamma"):
        save_env(name, SAMPLE_ENV, OLD_PASS)
    rotated = rotate_all(OLD_PASS, NEW_PASS)
    assert set(rotated) == {"alpha", "beta", "gamma"}
    for name in ("alpha", "beta", "gamma"):
        assert load_env(name, NEW_PASS) == SAMPLE_ENV


def test_rotate_all_empty_store_returns_empty_list(store):
    rotated = rotate_all(OLD_PASS, NEW_PASS)
    assert rotated == []


def test_rotate_all_stops_on_first_bad_password(store):
    save_env("first", SAMPLE_ENV, OLD_PASS)
    save_env("second", SAMPLE_ENV, "different-pass")
    with pytest.raises(Exception):
        rotate_all(OLD_PASS, NEW_PASS)
