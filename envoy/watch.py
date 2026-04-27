"""Watch a .env file for changes and auto-sync to the store."""

import os
import time
import hashlib
from pathlib import Path
from typing import Callable, Optional

from envoy.storage import save_env, load_env
from envoy.audit import record


def _file_hash(path: Path) -> str:
    """Return MD5 hex digest of file contents."""
    data = path.read_bytes()
    return hashlib.md5(data).hexdigest()


def _read_env_file(path: Path) -> str:
    """Read and return the contents of an env file."""
    return path.read_text(encoding="utf-8")


def watch_file(
    path: str,
    project: str,
    password: str,
    interval: float = 1.0,
    on_change: Optional[Callable[[str], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Watch *path* for changes and persist to *project* in the store.

    Args:
        path: Absolute or relative path to the .env file.
        project: Project name in the envoy store.
        password: Encryption password.
        interval: Polling interval in seconds.
        on_change: Optional callback invoked with the new env text on each change.
        max_iterations: Stop after this many poll cycles (useful for testing).
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    last_hash = _file_hash(env_path)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        iterations += 1

        try:
            current_hash = _file_hash(env_path)
        except FileNotFoundError:
            continue

        if current_hash != last_hash:
            last_hash = current_hash
            env_text = _read_env_file(env_path)
            save_env(project, env_text, password)
            record(project, "watch_sync", {"file": str(env_path)})
            if on_change:
                on_change(env_text)
