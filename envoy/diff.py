"""Diff utilities for comparing .env file contents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def _parse_env(text: str) -> Dict[str, str]:
    """Parse a .env-style string into a key/value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def diff_envs(old: str, new: str) -> DiffResult:
    """Compute the diff between two .env file contents."""
    old_map = _parse_env(old)
    new_map = _parse_env(new)

    result = DiffResult()

    all_keys = set(old_map) | set(new_map)
    for key in sorted(all_keys):
        in_old = key in old_map
        in_new = key in new_map
        if in_old and in_new:
            if old_map[key] == new_map[key]:
                result.unchanged[key] = old_map[key]
            else:
                result.changed[key] = (old_map[key], new_map[key])
        elif in_new:
            result.added[key] = new_map[key]
        else:
            result.removed[key] = old_map[key]

    return result


def format_diff(result: DiffResult) -> List[str]:
    """Return a list of human-readable diff lines."""
    lines: List[str] = []
    for key, value in sorted(result.added.items()):
        lines.append(f"+ {key}={value}")
    for key, value in sorted(result.removed.items()):
        lines.append(f"- {key}={value}")
    for key, (old_val, new_val) in sorted(result.changed.items()):
        lines.append(f"~ {key}: {old_val!r} -> {new_val!r}")
    return lines
