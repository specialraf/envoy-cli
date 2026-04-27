"""Tests for envoy.tag and envoy.cli_tag."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy import tag as tag_mod
from envoy.cli_tag import tag_cmd


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    monkeypatch.setattr("envoy.config._get_config_path", lambda: cfg_file)
    yield cfg_file


@pytest.fixture
def runner():
    return CliRunner()


# --- unit tests ---

def test_add_tag_returns_list():
    result = tag_mod.add_tag("myproject", "production")
    assert "production" in result


def test_add_tag_no_duplicates():
    tag_mod.add_tag("myproject", "staging")
    result = tag_mod.add_tag("myproject", "staging")
    assert result.count("staging") == 1


def test_list_tags_empty_initially():
    assert tag_mod.list_tags("unknown") == []


def test_list_tags_after_add():
    tag_mod.add_tag("proj", "alpha")
    tag_mod.add_tag("proj", "beta")
    tags = tag_mod.list_tags("proj")
    assert "alpha" in tags
    assert "beta" in tags


def test_remove_tag_removes_correctly():
    tag_mod.add_tag("proj", "v1")
    tag_mod.add_tag("proj", "v2")
    result = tag_mod.remove_tag("proj", "v1")
    assert "v1" not in result
    assert "v2" in result


def test_projects_with_tag_finds_correct_projects():
    tag_mod.add_tag("alpha", "prod")
    tag_mod.add_tag("beta", "staging")
    tag_mod.add_tag("gamma", "prod")
    projects = tag_mod.projects_with_tag("prod")
    assert "alpha" in projects
    assert "gamma" in projects
    assert "beta" not in projects


def test_clear_tags_removes_all():
    tag_mod.add_tag("proj", "x")
    tag_mod.add_tag("proj", "y")
    tag_mod.clear_tags("proj")
    assert tag_mod.list_tags("proj") == []


# --- CLI tests ---

def test_cli_add_tag(runner):
    result = runner.invoke(tag_cmd, ["add", "myproj", "prod"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_cli_list_tags(runner):
    tag_mod.add_tag("myproj", "staging")
    result = runner.invoke(tag_cmd, ["list", "myproj"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_cli_find_tag(runner):
    tag_mod.add_tag("proj-a", "shared")
    result = runner.invoke(tag_cmd, ["find", "shared"])
    assert result.exit_code == 0
    assert "proj-a" in result.output


def test_cli_list_empty(runner):
    result = runner.invoke(tag_cmd, ["list", "nonexistent"])
    assert result.exit_code == 0
    assert "No tags" in result.output
