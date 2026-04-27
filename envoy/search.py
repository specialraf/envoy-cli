"""Search across stored .env projects for keys or values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envoy.storage import list_projects, load_env


@dataclass
class SearchMatch:
    project: str
    key: str
    value: str
    matched_on: str  # 'key' | 'value' | 'both'


@dataclass
class SearchResult:
    query: str
    matches: List[SearchMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return len(self.matches) > 0


def _parse_env(raw: str) -> dict[str, str]:
    """Parse a dotenv string into a key/value dict."""
    result: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def search_projects(
    query: str,
    password: str,
    *,
    project: Optional[str] = None,
    keys_only: bool = False,
    values_only: bool = False,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search all (or a specific) project for a query string.

    Args:
        query: The string to search for.
        password: Master password used to decrypt env data.
        project: If given, restrict search to this project only.
        keys_only: Only match against keys.
        values_only: Only match against values.
        case_sensitive: Whether the match is case-sensitive.

    Returns:
        A SearchResult containing all matches found.
    """
    result = SearchResult(query=query)
    needle = query if case_sensitive else query.lower()

    projects = [project] if project else list_projects()

    for proj in projects:
        try:
            raw = load_env(proj, password)
        except (KeyError, ValueError):
            continue

        env = _parse_env(raw)
        for key, value in env.items():
            k = key if case_sensitive else key.lower()
            v = value if case_sensitive else value.lower()

            key_hit = not values_only and needle in k
            val_hit = not keys_only and needle in v

            if key_hit and val_hit:
                matched_on = "both"
            elif key_hit:
                matched_on = "key"
            elif val_hit:
                matched_on = "value"
            else:
                continue

            result.matches.append(
                SearchMatch(project=proj, key=key, value=value, matched_on=matched_on)
            )

    return result
