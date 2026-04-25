"""Template support: generate .env files from a template with placeholders."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class TemplateVar:
    name: str
    required: bool = True
    default: Optional[str] = None
    description: str = ""


@dataclass
class ParsedTemplate:
    raw: str
    variables: List[TemplateVar] = field(default_factory=list)


def parse_template(text: str) -> ParsedTemplate:
    """Extract placeholder variables from a template string."""
    seen: Dict[str, TemplateVar] = {}
    for match in _PLACEHOLDER_RE.finditer(text):
        name = match.group(1)
        if name not in seen:
            seen[name] = TemplateVar(name=name)
    return ParsedTemplate(raw=text, variables=list(seen.values()))


def render_template(template: ParsedTemplate, values: Dict[str, str]) -> str:
    """Render a template by substituting placeholder values.

    Raises KeyError if a required variable has no value and no default.
    """
    result = template.raw
    for var in template.variables:
        value = values.get(var.name)
        if value is None:
            if var.default is not None:
                value = var.default
            elif var.required:
                raise KeyError(f"Missing required template variable: {var.name!r}")
            else:
                value = ""
        result = re.sub(r"\{\{\s*" + re.escape(var.name) + r"\s*\}\}", value, result)
    return result


def template_from_env(env_text: str) -> str:
    """Convert an existing .env file into a template by replacing values with placeholders."""
    lines = []
    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines.append(line)
            continue
        key, _ = stripped.split("=", 1)
        lines.append(f"{key.strip()}={{{{ {key.strip()} }}}}")
    return "\n".join(lines)
