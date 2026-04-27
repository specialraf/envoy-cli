"""Merge two env projects or an env file into a stored project."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.storage import load_env, save_env


@dataclass
class MergeResult:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    final_env: Dict[str, str] = field(default_factory=dict)


def _parse_env(text: str) -> Dict[str, str]:
    """Parse a .env-style string into a dict, skipping comments and blanks."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def merge_projects(
    base_project: str,
    overlay_project: str,
    password: str,
    *,
    overwrite: bool = False,
    store_path: Optional[str] = None,
) -> MergeResult:
    """Merge *overlay_project* into *base_project*.

    Keys present only in overlay are added.  Keys present in both are updated
    only when *overwrite* is True, otherwise they are skipped.
    """
    kwargs = {"store_path": store_path} if store_path else {}
    base_text = load_env(base_project, password, **kwargs)
    overlay_text = load_env(overlay_project, password, **kwargs)

    base = _parse_env(base_text)
    overlay = _parse_env(overlay_text)

    result = MergeResult()
    merged = dict(base)

    for key, value in overlay.items():
        if key not in base:
            merged[key] = value
            result.added.append(key)
        elif overwrite and base[key] != value:
            merged[key] = value
            result.updated.append(key)
        else:
            result.skipped.append(key)

    result.final_env = merged
    new_text = "\n".join(f"{k}={v}" for k, v in merged.items())
    save_env(base_project, new_text, password, **kwargs)
    return result


def merge_file(
    project: str,
    env_text: str,
    password: str,
    *,
    overwrite: bool = False,
    store_path: Optional[str] = None,
) -> MergeResult:
    """Merge a raw .env string into *project*."""
    kwargs = {"store_path": store_path} if store_path else {}
    base_text = load_env(project, password, **kwargs)
    base = _parse_env(base_text)
    overlay = _parse_env(env_text)

    result = MergeResult()
    merged = dict(base)

    for key, value in overlay.items():
        if key not in base:
            merged[key] = value
            result.added.append(key)
        elif overwrite and base[key] != value:
            merged[key] = value
            result.updated.append(key)
        else:
            result.skipped.append(key)

    result.final_env = merged
    new_text = "\n".join(f"{k}={v}" for k, v in merged.items())
    save_env(project, new_text, password, **kwargs)
    return result
