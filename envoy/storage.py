"""Local encrypted storage for .env files."""

import json
import os
from pathlib import Path
from typing import Optional

from envoy.crypto import encrypt, decrypt

DEFAULT_STORE_DIR = Path.home() / ".envoy"
STORE_FILE = "store.json"


def _get_store_path(store_dir: Optional[Path] = None) -> Path:
    """Return the path to the encrypted store file."""
    base = store_dir or DEFAULT_STORE_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / STORE_FILE


def _load_raw(store_dir: Optional[Path] = None) -> dict:
    """Load the raw store dict from disk (values are hex-encoded ciphertext)."""
    path = _get_store_path(store_dir)
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_raw(data: dict, store_dir: Optional[Path] = None) -> None:
    """Persist the raw store dict to disk."""
    path = _get_store_path(store_dir)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def save_env(project: str, env_content: str, password: str,
             store_dir: Optional[Path] = None) -> None:
    """Encrypt and save an env file for *project*."""
    ciphertext = encrypt(env_content.encode(), password)
    data = _load_raw(store_dir)
    data[project] = ciphertext.hex()
    _save_raw(data, store_dir)


def load_env(project: str, password: str,
             store_dir: Optional[Path] = None) -> str:
    """Load and decrypt the env file for *project*.

    Raises KeyError if the project does not exist.
    """
    data = _load_raw(store_dir)
    if project not in data:
        raise KeyError(f"No stored env for project '{project}'")
    ciphertext = bytes.fromhex(data[project])
    return decrypt(ciphertext, password).decode()


def list_projects(store_dir: Optional[Path] = None) -> list[str]:
    """Return a sorted list of stored project names."""
    return sorted(_load_raw(store_dir).keys())


def delete_env(project: str, store_dir: Optional[Path] = None) -> None:
    """Remove the stored env for *project*.

    Raises KeyError if the project does not exist.
    """
    data = _load_raw(store_dir)
    if project not in data:
        raise KeyError(f"No stored env for project '{project}'")
    del data[project]
    _save_raw(data, store_dir)
