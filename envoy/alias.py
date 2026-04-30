"""Project alias management — assign short names to projects."""

from __future__ import annotations

from typing import Dict, List, Optional

from envoy.config import get_value, set_value

_ALIAS_KEY = "aliases"


def _get_all_aliases() -> Dict[str, str]:
    """Return the full alias -> project mapping."""
    raw = get_value(_ALIAS_KEY)
    if not isinstance(raw, dict):
        return {}
    return dict(raw)


def _save_aliases(aliases: Dict[str, str]) -> None:
    set_value(_ALIAS_KEY, aliases)


def add_alias(alias: str, project: str) -> Dict[str, str]:
    """Map *alias* to *project*. Returns the updated alias map."""
    alias = alias.strip()
    project = project.strip()
    if not alias:
        raise ValueError("Alias must not be empty.")
    if not project:
        raise ValueError("Project name must not be empty.")
    aliases = _get_all_aliases()
    aliases[alias] = project
    _save_aliases(aliases)
    return aliases


def remove_alias(alias: str) -> Dict[str, str]:
    """Remove *alias*. Raises KeyError if it does not exist."""
    aliases = _get_all_aliases()
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(aliases)
    return aliases


def resolve_alias(alias: str) -> Optional[str]:
    """Return the project name for *alias*, or None if not set."""
    return _get_all_aliases().get(alias)


def list_aliases() -> List[Dict[str, str]]:
    """Return a sorted list of {alias, project} dicts."""
    aliases = _get_all_aliases()
    return [
        {"alias": a, "project": p}
        for a, p in sorted(aliases.items())
    ]


def aliases_for_project(project: str) -> List[str]:
    """Return all alias names that point to *project*."""
    return [
        a for a, p in _get_all_aliases().items() if p == project
    ]
