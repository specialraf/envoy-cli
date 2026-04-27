"""Snapshot support: save and restore point-in-time copies of a project's env."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envoy.storage import load_env, save_env


def _get_snapshot_dir(store_path: Path, project: str) -> Path:
    snap_dir = store_path / "snapshots" / project
    snap_dir.mkdir(parents=True, exist_ok=True)
    return snap_dir


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_snapshot(
    store_path: Path,
    project: str,
    password: str,
    label: Optional[str] = None,
) -> str:
    """Snapshot the current env for *project* and return the snapshot name."""
    env_content = load_env(store_path, project, password)
    snap_dir = _get_snapshot_dir(store_path, project)
    name = label if label else _now_iso()
    meta = {"name": name, "created_at": _now_iso(), "label": label or ""}
    (snap_dir / f"{name}.env").write_text(env_content, encoding="utf-8")
    (snap_dir / f"{name}.json").write_text(json.dumps(meta), encoding="utf-8")
    return name


def list_snapshots(store_path: Path, project: str) -> List[dict]:
    """Return metadata dicts for all snapshots of *project*, newest first."""
    snap_dir = _get_snapshot_dir(store_path, project)
    metas = []
    for meta_file in sorted(snap_dir.glob("*.json"), reverse=True):
        try:
            metas.append(json.loads(meta_file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return metas


def restore_snapshot(
    store_path: Path,
    project: str,
    name: str,
    password: str,
) -> None:
    """Overwrite the live env for *project* with the named snapshot."""
    snap_dir = _get_snapshot_dir(store_path, project)
    env_file = snap_dir / f"{name}.env"
    if not env_file.exists():
        raise KeyError(f"Snapshot '{name}' not found for project '{project}'")
    env_content = env_file.read_text(encoding="utf-8")
    save_env(store_path, project, password, env_content)


def delete_snapshot(store_path: Path, project: str, name: str) -> None:
    """Delete a snapshot by name."""
    snap_dir = _get_snapshot_dir(store_path, project)
    removed = False
    for ext in (".env", ".json"):
        f = snap_dir / f"{name}{ext}"
        if f.exists():
            f.unlink()
            removed = True
    if not removed:
        raise KeyError(f"Snapshot '{name}' not found for project '{project}'")
