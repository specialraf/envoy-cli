"""Tests for envoy.cli_alias."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.cli_alias import alias_cmd


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    monkeypatch.setattr("envoy.config._get_config_path", lambda: cfg_file)
    yield cfg_file


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


def test_add_prints_confirmation(runner):
    result = runner.invoke(alias_cmd, ["add", "prod", "my-app"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "my-app" in result.output


def test_remove_existing_alias(runner):
    runner.invoke(alias_cmd, ["add", "dev", "dev-app"])
    result = runner.invoke(alias_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_alias_fails(runner):
    result = runner.invoke(alias_cmd, ["remove", "ghost"])
    assert result.exit_code != 0


def test_resolve_existing_alias(runner):
    runner.invoke(alias_cmd, ["add", "staging", "staging-app"])
    result = runner.invoke(alias_cmd, ["resolve", "staging"])
    assert result.exit_code == 0
    assert "staging-app" in result.output


def test_resolve_missing_alias_fails(runner):
    result = runner.invoke(alias_cmd, ["resolve", "nope"])
    assert result.exit_code != 0


def test_list_empty(runner):
    result = runner.invoke(alias_cmd, ["list"])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_list_shows_aliases(runner):
    runner.invoke(alias_cmd, ["add", "a", "alpha"])
    runner.invoke(alias_cmd, ["add", "b", "beta"])
    result = runner.invoke(alias_cmd, ["list"])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "alpha" in result.output


def test_find_aliases_for_project(runner):
    runner.invoke(alias_cmd, ["add", "x", "shared"])
    runner.invoke(alias_cmd, ["add", "y", "shared"])
    result = runner.invoke(alias_cmd, ["find", "shared"])
    assert result.exit_code == 0
    assert "x" in result.output
    assert "y" in result.output


def test_find_no_aliases(runner):
    result = runner.invoke(alias_cmd, ["find", "unknown"])
    assert result.exit_code == 0
    assert "No aliases" in result.output
