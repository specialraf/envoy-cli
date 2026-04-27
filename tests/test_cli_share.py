"""Tests for envoy.cli_share CLI commands."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envoy.cli_share import share_cmd


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("ENVOY_SHARE_DIR", str(tmp_path / "shares"))
    from envoy.storage import save_env
    save_env("proj", {"A": "1", "B": "2"}, "secret")
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_create_prints_token(store, runner):
    result = runner.invoke(share_cmd, ["create", "proj"], input="secret\n")
    assert result.exit_code == 0
    assert "Share token" in result.output


def test_create_unknown_key_fails(store, runner):
    result = runner.invoke(share_cmd, ["create", "proj", "--keys", "NOPE"], input="secret\n")
    assert result.exit_code != 0
    assert "NOPE" in result.output


def test_redeem_dotenv_format(store, runner):
    from envoy.share import create_share
    token = create_share("proj", "secret")
    result = runner.invoke(share_cmd, ["redeem", token])
    assert result.exit_code == 0
    assert "A=1" in result.output
    assert "B=2" in result.output


def test_redeem_json_format(store, runner):
    from envoy.share import create_share
    token = create_share("proj", "secret")
    result = runner.invoke(share_cmd, ["redeem", token, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["A"] == "1"


def test_redeem_invalid_token_fails(store, runner):
    result = runner.invoke(share_cmd, ["redeem", "badtoken"])
    assert result.exit_code != 0


def test_redeem_revoked_token_fails(store, runner):
    """Redeeming a token after it has been revoked should fail."""
    from envoy.share import create_share
    token = create_share("proj", "secret")
    runner.invoke(share_cmd, ["revoke", token])
    result = runner.invoke(share_cmd, ["redeem", token])
    assert result.exit_code != 0


def test_revoke_success(store, runner):
    from envoy.share import create_share
    token = create_share("proj", "secret")
    result = runner.invoke(share_cmd, ["revoke", token])
    assert result.exit_code == 0
    assert "revoked" in result.output.lower()


def test_revoke_missing_token_fails(store, runner):
    result = runner.invoke(share_cmd, ["revoke", "notatoken"])
    assert result.exit_code != 0


def test_list_shows_active_tokens(store, runner):
    from envoy.share import create_share
    token = create_share("proj", "secret")
    result = runner.invoke(share_cmd, ["list"])
    assert result.exit_code == 0
    assert token[:12] in result.output


def test_list_empty_message(store, runner):
    result = runner.invoke(share_cmd, ["list"])
    assert result.exit_code == 0
    assert "No active" in result.output
