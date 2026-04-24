"""Tests for the config CLI sub-commands."""

import pytest
from click.testing import CliRunner

from envoy.cli_config import config_cmd
from envoy.config import load_config, save_config, DEFAULT_CONFIG


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setenv("ENVOY_CONFIG_PATH", str(config_file))
    yield config_file


@pytest.fixture
def runner():
    return CliRunner()


def test_config_set_updates_value(runner):
    result = runner.invoke(config_cmd, ["set", "remote_url", "https://example.com"])
    assert result.exit_code == 0
    assert "Config updated" in result.output
    assert load_config()["remote_url"] == "https://example.com"


def test_config_set_unknown_key_fails(runner):
    result = runner.invoke(config_cmd, ["set", "bad_key", "val"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_config_set_timeout_coerces_to_int(runner):
    result = runner.invoke(config_cmd, ["set", "timeout", "30"])
    assert result.exit_code == 0
    assert load_config()["timeout"] == 30


def test_config_set_timeout_invalid_value(runner):
    result = runner.invoke(config_cmd, ["set", "timeout", "fast"])
    assert result.exit_code != 0
    assert "expected a number" in result.output


def test_config_get_returns_value(runner):
    cfg = dict(DEFAULT_CONFIG)
    cfg["remote_url"] = "https://stored.example.com"
    save_config(cfg)
    result = runner.invoke(config_cmd, ["get", "remote_url"])
    assert result.exit_code == 0
    assert "https://stored.example.com" in result.output


def test_config_get_unknown_key_fails(runner):
    result = runner.invoke(config_cmd, ["get", "ghost_key"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_config_list_shows_all_keys(runner):
    result = runner.invoke(config_cmd, ["list"])
    assert result.exit_code == 0
    for key in DEFAULT_CONFIG:
        assert key in result.output


def test_config_list_masks_token(runner):
    cfg = dict(DEFAULT_CONFIG)
    cfg["token"] = "supersecret"
    save_config(cfg)
    result = runner.invoke(config_cmd, ["list"])
    assert "supersecret" not in result.output
    assert "****" in result.output
