"""Remote sync support for envoy: push/pull encrypted .env files to/from a remote store."""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Optional

REMOTE_URL_ENV = "ENVOY_REMOTE_URL"
REMOTE_TOKEN_ENV = "ENVOY_REMOTE_TOKEN"


def _get_remote_url() -> str:
    url = os.environ.get(REMOTE_URL_ENV, "").rstrip("/")
    if not url:
        raise EnvironmentError(
            f"Remote URL not configured. Set the {REMOTE_URL_ENV} environment variable."
        )
    return url


def _get_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    token = os.environ.get(REMOTE_TOKEN_ENV, "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def push(project: str, encrypted_blob: bytes) -> None:
    """Upload an encrypted blob for *project* to the remote store."""
    url = f"{_get_remote_url()}/envs/{project}"
    payload = json.dumps({"data": encrypted_blob.hex()}).encode()
    req = urllib.request.Request(url, data=payload, headers=_get_headers(), method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Push failed ({exc.code}): {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Push failed: {exc.reason}") from exc


def pull(project: str) -> bytes:
    """Download and return the encrypted blob for *project* from the remote store."""
    url = f"{_get_remote_url()}/envs/{project}"
    req = urllib.request.Request(url, headers=_get_headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return bytes.fromhex(body["data"])
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise KeyError(f"Project '{project}' not found on remote.") from exc
        raise RuntimeError(f"Pull failed ({exc.code}): {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Pull failed: {exc.reason}") from exc
