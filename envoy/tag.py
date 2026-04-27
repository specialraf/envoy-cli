"""Tag management for env projects — assign and filter projects by tags."""

from __future__ import annotations

from typing import List

from envoy.config import get_value, set_value, load_config, save_config

_TAGS_KEY = "project_tags"


def _get_all_tags(config: dict) -> dict:
    """Return the project->tags mapping from config, defaulting to {}."""
    return config.get(_TAGS_KEY, {})


def add_tag(project: str, tag: str) -> List[str]:
    """Add *tag* to *project*. Returns the updated tag list."""
    from envoy.config import _get_config_path
    import json

    config = load_config()
    tags_map: dict = config.get(_TAGS_KEY, {})
    current: List[str] = tags_map.get(project, [])
    if tag not in current:
        current.append(tag)
    tags_map[project] = current
    config[_TAGS_KEY] = tags_map
    save_config(config)
    return current


def remove_tag(project: str, tag: str) -> List[str]:
    """Remove *tag* from *project*. Returns the updated tag list."""
    config = load_config()
    tags_map: dict = config.get(_TAGS_KEY, {})
    current: List[str] = tags_map.get(project, [])
    current = [t for t in current if t != tag]
    tags_map[project] = current
    config[_TAGS_KEY] = tags_map
    save_config(config)
    return current


def list_tags(project: str) -> List[str]:
    """Return all tags assigned to *project*."""
    config = load_config()
    return config.get(_TAGS_KEY, {}).get(project, [])


def projects_with_tag(tag: str) -> List[str]:
    """Return all project names that carry *tag*."""
    config = load_config()
    tags_map: dict = config.get(_TAGS_KEY, {})
    return [proj for proj, tags in tags_map.items() if tag in tags]


def clear_tags(project: str) -> None:
    """Remove every tag from *project*."""
    config = load_config()
    tags_map: dict = config.get(_TAGS_KEY, {})
    tags_map.pop(project, None)
    config[_TAGS_KEY] = tags_map
    save_config(config)
