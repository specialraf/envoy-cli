"""Tests for envoy.sync — remote push/pull logic."""

from __future__ import annotations

import json
import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from envoy.sync import pull, push

FAKE_URL = "https://envoy.example.com"
FAKE_TOKEN = "secret-token"
BLOB = b"encrypted-payload-bytes"


@pytest.fixture(autouse=True)
def remote_env(monkeypatch):
    monkeypatch.setenv("ENVOY_REMOTE_URL", FAKE_URL)
    monkeypatch.setenv("ENVOY_REMOTE_TOKEN", FAKE_TOKEN)


def _make_response(body: dict, status: int = 200):
    raw = json.dumps(body).encode()
    resp = MagicMock()
    resp.read.return_value = raw
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_push_calls_correct_url():
    with patch("urllib.request.urlopen") as mock_open:
        mock_open.return_value = _make_response({})
        push("myproject", BLOB)
        args, _ = mock_open.call_args
        req = args[0]
        assert req.full_url == f"{FAKE_URL}/envs/myproject"
        assert req.method == "PUT"


def test_push_sends_hex_encoded_blob():
    with patch("urllib.request.urlopen") as mock_open:
        mock_open.return_value = _make_response({})
        push("myproject", BLOB)
        args, _ = mock_open.call_args
        req = args[0]
        body = json.loads(req.data)
        assert body["data"] == BLOB.hex()


def test_pull_returns_blob():
    with patch("urllib.request.urlopen") as mock_open:
        mock_open.return_value = _make_response({"data": BLOB.hex()})
        result = pull("myproject")
        assert result == BLOB


def test_pull_404_raises_key_error():
    import urllib.error

    with patch("urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.HTTPError(
            url=None, code=404, msg="Not Found", hdrs=None, fp=None
        )
        with pytest.raises(KeyError, match="myproject"):
            pull("myproject")


def test_missing_remote_url_raises(monkeypatch):
    monkeypatch.delenv("ENVOY_REMOTE_URL", raising=False)
    with pytest.raises(EnvironmentError, match="ENVOY_REMOTE_URL"):
        push("myproject", BLOB)


def test_auth_header_included():
    with patch("urllib.request.urlopen") as mock_open:
        mock_open.return_value = _make_response({})
        push("myproject", BLOB)
        args, _ = mock_open.call_args
        req = args[0]
        assert req.get_header("Authorization") == f"Bearer {FAKE_TOKEN}"
