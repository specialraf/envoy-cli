"""Tests for envoy.share module."""

import time
import pytest
from unittest.mock import patch

from envoy.share import create_share, redeem_share, revoke_share, list_shares


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("ENVOY_SHARE_DIR", str(tmp_path / "shares"))
    from envoy.storage import save_env
    save_env("myproject", {"KEY": "value", "SECRET": "s3cr3t"}, "pass")
    return tmp_path


def test_create_share_returns_token(store):
    token = create_share("myproject", "pass")
    assert isinstance(token, str)
    assert len(token) == 48  # 24 bytes hex


def test_redeem_share_returns_env(store):
    token = create_share("myproject", "pass")
    env = redeem_share(token)
    assert env["KEY"] == "value"
    assert env["SECRET"] == "s3cr3t"


def test_create_share_with_specific_keys(store):
    token = create_share("myproject", "pass", keys=["KEY"])
    env = redeem_share(token)
    assert "KEY" in env
    assert "SECRET" not in env


def test_create_share_unknown_key_raises(store):
    with pytest.raises(KeyError, match="MISSING"):
        create_share("myproject", "pass", keys=["MISSING"])


def test_redeem_missing_token_raises(store):
    with pytest.raises(KeyError):
        redeem_share("nonexistent_token_abc123")


def test_redeem_expired_token_raises(store):
    token = create_share("myproject", "pass", ttl=1)
    with patch("envoy.share.time.time", return_value=time.time() + 9999):
        with pytest.raises(PermissionError, match="expired"):
            redeem_share(token)


def test_revoke_share_removes_token(store):
    token = create_share("myproject", "pass")
    revoke_share(token)
    with pytest.raises(KeyError):
        redeem_share(token)


def test_revoke_missing_token_raises(store):
    with pytest.raises(KeyError):
        revoke_share("no_such_token")


def test_list_shares_returns_active(store):
    token = create_share("myproject", "pass", ttl=3600)
    shares = list_shares()
    tokens = [s["token"] for s in shares]
    assert token in tokens


def test_list_shares_excludes_expired(store):
    token = create_share("myproject", "pass", ttl=1)
    with patch("envoy.share.time.time", return_value=time.time() + 9999):
        shares = list_shares()
    tokens = [s["token"] for s in shares]
    assert token not in tokens


def test_each_token_is_unique(store):
    t1 = create_share("myproject", "pass")
    t2 = create_share("myproject", "pass")
    assert t1 != t2
