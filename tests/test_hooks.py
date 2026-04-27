"""Tests for envoy.hooks."""

from __future__ import annotations

import pytest

from envoy.hooks import (
    HOOK_KEYS,
    HookResult,
    clear_hook,
    get_hook,
    list_hooks,
    run_hook,
    set_hook,
)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Redirect config to a temp directory for every test."""
    monkeypatch.setenv("ENVOY_CONFIG_DIR", str(tmp_path))
    yield tmp_path


def test_get_hook_returns_none_when_unset():
    assert get_hook("pre_push") is None


def test_set_and_get_hook_roundtrip():
    set_hook("post_push", "echo pushed")
    assert get_hook("post_push") == "echo pushed"


def test_clear_hook_removes_command():
    set_hook("pre_pull", "echo before pull")
    clear_hook("pre_pull")
    assert get_hook("pre_pull") is None


def test_get_hook_unknown_raises():
    with pytest.raises(ValueError, match="Unknown hook"):
        get_hook("on_explode")


def test_set_hook_unknown_raises():
    with pytest.raises(ValueError, match="Unknown hook"):
        set_hook("on_explode", "rm -rf /")


def test_clear_hook_unknown_raises():
    with pytest.raises(ValueError, match="Unknown hook"):
        clear_hook("on_explode")


def test_run_hook_returns_none_when_unset():
    result = run_hook("pre_set")
    assert result is None


def test_run_hook_executes_command():
    set_hook("post_set", "echo hello")
    result = run_hook("post_set")
    assert isinstance(result, HookResult)
    assert result.ok
    assert "hello" in result.stdout


def test_run_hook_captures_failure():
    set_hook("pre_push", "exit 42")
    result = run_hook("pre_push")
    assert result is not None
    assert result.returncode == 42
    assert not result.ok


def test_run_hook_unknown_raises():
    """run_hook should reject unknown hook names, consistent with get/set/clear."""
    with pytest.raises(ValueError, match="Unknown hook"):
        run_hook("on_explode")


def test_list_hooks_returns_all_keys():
    hooks = list_hooks()
    hook_names = {h["hook"] for h in hooks}
    assert hook_names == HOOK_KEYS


def test_list_hooks_shows_registered_command():
    set_hook("post_pull", "make sync")
    hooks = {h["hook"]: h["command"] for h in list_hooks()}
    assert hooks["post_pull"] == "make sync"


def test_list_hooks_empty_when_none_set():
    hooks = list_hooks()
    for h in hooks:
        assert h["command"] == ""
