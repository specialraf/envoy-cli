"""Tests for envoy.config module."""

import json
import pytest
from pathlib import Path

from envoy.config import (
    load_config,
    save_config,
    get_value,
    set_value,
    DEFAULT_CONFIG,
)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Redirect config path to a temp directory for every test."""
    config_file = tmp_path / "config.json"
    monkeypatch.setenv("ENVOY_CONFIG_PATH", str(config_file))
    yield config_file


def test_load_config_returns_defaults_when_missing():
    config = load_config()
    assert config == DEFAULT_CONFIG


def test_save_and_load_roundtrip(isolated_config):
    data = dict(DEFAULT_CONFIG)
    data["remote_url"] = "https://example.com"
    save_config(data)
    loaded = load_config()
    assert loaded["remote_url"] == "https://example.com"


def test_load_config_merges_missing_keys(isolated_config):
    """Partial config on disk should be filled in with defaults."""
    isolated_config.write_text(json.dumps({"remote_url": "https://x.io"}))
    config = load_config()
    assert config["remote_url"] == "https://x.io"
    assert config["timeout"] == DEFAULT_CONFIG["timeout"]


def test_load_config_handles_corrupt_file(isolated_config):
    isolated_config.write_text("not valid json{{")
    config = load_config()
    assert config == DEFAULT_CONFIG


def test_get_value_returns_correct_value():
    config = dict(DEFAULT_CONFIG)
    config["token"] = "abc123"
    save_config(config)
    assert get_value("token") == "abc123"


def test_get_value_missing_key_returns_none():
    assert get_value("nonexistent_key") is None


def test_set_value_persists_change():
    set_value("remote_url", "https://new.example.com")
    assert get_value("remote_url") == "https://new.example.com"


def test_set_value_unknown_key_raises():
    with pytest.raises(KeyError, match="Unknown config key"):
        set_value("invalid_key", "value")


def test_save_config_creates_parent_dirs(tmp_path, monkeypatch):
    nested = tmp_path / "a" / "b" / "c" / "config.json"
    monkeypatch.setenv("ENVOY_CONFIG_PATH", str(nested))
    save_config(dict(DEFAULT_CONFIG))
    assert nested.exists()
