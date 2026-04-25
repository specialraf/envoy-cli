"""Backup and restore encrypted .env snapshots to/from local archive files."""

from __future__ import annotations

import json
import tarfile
import io
import time
from pathlib import Path
from typing import Optional

from envoy.storage import load_env, save_env, list_projects


def _timestamp() -> str:
    return time.strftime("%Y%m%dT%H%M%S")


def backup_all(password: str, dest_dir: Path) -> Path:
    """Backup all projects to a timestamped .tar archive in dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"envoy-backup-{_timestamp()}.tar"

    projects = list_projects()
    if not projects:
        raise ValueError("No projects found to back up.")

    with tarfile.open(archive_path, "w") as tar:
        for project in projects:
            env_vars = load_env(project, password)
            data = json.dumps(env_vars).encode()
            info = tarfile.TarInfo(name=f"{project}.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

    return archive_path


def restore_all(password: str, archive_path: Path, overwrite: bool = False) -> list[str]:
    """Restore projects from a backup archive. Returns list of restored project names."""
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    existing = set(list_projects())
    restored: list[str] = []

    with tarfile.open(archive_path, "r") as tar:
        for member in tar.getmembers():
            project = member.name.removesuffix(".json")
            if project in existing and not overwrite:
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            env_vars = json.loads(f.read().decode())
            save_env(project, env_vars, password)
            restored.append(project)

    return restored
