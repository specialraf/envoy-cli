"""Export and import .env files in various formats (dotenv, JSON, shell)."""

from __future__ import annotations

import json
import re
from typing import Dict

SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def _parse_env(text: str) -> Dict[str, str]:
    """Parse dotenv-style text into a key/value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            result[key] = value
    return result


def export_env(text: str, fmt: str) -> str:
    """Convert dotenv text to the requested format."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    pairs = _parse_env(text)

    if fmt == "dotenv":
        return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"

    if fmt == "json":
        return json.dumps(pairs, indent=2) + "\n"

    if fmt == "shell":
        lines = [f'export {k}="{v}"' for k, v in pairs.items()]
        return "\n".join(lines) + "\n"

    raise ValueError(f"Unhandled format: {fmt}")  # pragma: no cover


def import_env(text: str, fmt: str) -> str:
    """Convert text in the given format back to dotenv format."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    if fmt == "dotenv":
        return export_env(text, "dotenv")

    if fmt == "json":
        try:
            pairs = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc
        if not isinstance(pairs, dict):
            raise ValueError("JSON must be a top-level object")
        lines = [f"{k}={v}" for k, v in pairs.items()]
        return "\n".join(lines) + "\n"

    if fmt == "shell":
        pairs: Dict[str, str] = {}
        pattern = re.compile(r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=["\']?([^"\']*)["\'\s]*$')
        for line in text.splitlines():
            m = pattern.match(line.strip())
            if m:
                pairs[m.group(1)] = m.group(2)
        lines = [f"{k}={v}" for k, v in pairs.items()]
        return "\n".join(lines) + "\n"

    raise ValueError(f"Unhandled format: {fmt}")  # pragma: no cover
