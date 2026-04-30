"""Tests for envoy.alias."""

from __future__ import annotations

import pytest

from envoy.alias import (
    add_alias,
    aliases_for_project,
    list_aliases,
    remove_alias,
    resolve_alias,
)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    monkeypatch.setattr("envoy.config._get_config_path", lambda: cfg_file)
    yield cfg_file


def test_add_alias_returns_mapping():
    result = add_alias("prod", "my-app")
    assert result["prod"] == "my-app"


def test_add_alias_no_duplicates_overwrites():
    add_alias("prod", "my-app")
    add_alias("prod", "other-app")
    assert resolve_alias("prod") == "other-app"


def test_resolve_alias_returns_project():
    add_alias("dev", "dev-project")
    assert resolve_alias("dev") == "dev-project"


def test_resolve_alias_missing_returns_none():
    assert resolve_alias("nonexistent") is None


def test_remove_alias_removes_entry():
    add_alias("staging", "staging-app")
    remove_alias("staging")
    assert resolve_alias("staging") is None


def test_remove_alias_missing_raises_key_error():
    with pytest.raises(KeyError, match="not found"):
        remove_alias("ghost")


def test_list_aliases_empty_initially():
    assert list_aliases() == []


def test_list_aliases_sorted():
    add_alias("z-alias", "z-proj")
    add_alias("a-alias", "a-proj")
    entries = list_aliases()
    assert entries[0]["alias"] == "a-alias"
    assert entries[1]["alias"] == "z-alias"


def test_aliases_for_project_returns_all():
    add_alias("p1", "shared")
    add_alias("p2", "shared")
    add_alias("other", "different")
    result = aliases_for_project("shared")
    assert sorted(result) == ["p1", "p2"]


def test_aliases_for_project_none_returns_empty():
    assert aliases_for_project("unknown") == []


def test_add_alias_empty_alias_raises():
    with pytest.raises(ValueError, match="empty"):
        add_alias("", "project")


def test_add_alias_empty_project_raises():
    with pytest.raises(ValueError, match="empty"):
        add_alias("alias", "")
