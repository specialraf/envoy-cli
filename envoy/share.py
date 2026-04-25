"""Share .env secrets with other users via time-limited tokens."""

import os
import json
import secrets
import time
from pathlib import Path
from typing import Optional

from envoy.storage import load_env

_TOKEN_DIR_NAME = ".envoy_shares"
_DEFAULT_TTL = 3600  # 1 hour


def _get_share_dir() -> Path:
    base = Path(os.environ.get("ENVOY_SHARE_DIR", Path.home() / _TOKEN_DIR_NAME))
    base.mkdir(parents=True, exist_ok=True)
    return base


def _token_path(token: str) -> Path:
    return _get_share_dir() / f"{token}.json"


def create_share(
    project: str,
    password: str,
    ttl: int = _DEFAULT_TTL,
    keys: Optional[list] = None,
) -> str:
    """Create a share token for a project's env vars.

    Args:
        project: Project name to share.
        password: Master password to decrypt the project.
        ttl: Seconds until the token expires.
        keys: Optional list of specific keys to share; None means all.

    Returns:
        A hex token string the recipient can use to retrieve the vars.
    """
    env = load_env(project, password)
    if keys is not None:
        missing = set(keys) - set(env)
        if missing:
            raise KeyError(f"Keys not found in project: {missing}")
        env = {k: env[k] for k in keys}

    token = secrets.token_hex(24)
    payload = {
        "project": project,
        "env": env,
        "expires_at": time.time() + ttl,
        "created_at": time.time(),
    }
    _token_path(token).write_text(json.dumps(payload))
    return token


def redeem_share(token: str) -> dict:
    """Redeem a share token and return the env vars.

    Raises:
        KeyError: If the token does not exist.
        PermissionError: If the token has expired.
    """
    path = _token_path(token)
    if not path.exists():
        raise KeyError(f"Share token not found: {token}")

    payload = json.loads(path.read_text())
    if time.time() > payload["expires_at"]:
        path.unlink(missing_ok=True)
        raise PermissionError("Share token has expired.")

    return payload["env"]


def revoke_share(token: str) -> None:
    """Delete a share token before it expires."""
    path = _token_path(token)
    if not path.exists():
        raise KeyError(f"Share token not found: {token}")
    path.unlink()


def list_shares() -> list:
    """Return metadata for all active (non-expired) share tokens."""
    shares = []
    for p in _get_share_dir().glob("*.json"):
        try:
            payload = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if time.time() <= payload["expires_at"]:
            shares.append({
                "token": p.stem,
                "project": payload["project"],
                "expires_at": payload["expires_at"],
                "created_at": payload["created_at"],
            })
    return shares
