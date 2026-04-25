"""Lint .env content for common issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    line_number: int
    line: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line_number}: {self.message!r} -> {self.line!r}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def __str__(self) -> str:
        if self.ok:
            return "No issues found."
        return "\n".join(str(i) for i in self.issues)


def lint_env(content: str) -> LintResult:
    """Lint raw .env text and return a LintResult with any issues."""
    result = LintResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()

        # Skip blanks and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(
                LintIssue(lineno, raw_line, "Missing '=' separator")
            )
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(
                LintIssue(lineno, raw_line, "Empty key")
            )
            continue

        if " " in key:
            result.issues.append(
                LintIssue(lineno, raw_line, "Key contains whitespace")
            )

        if key != key.upper():
            result.issues.append(
                LintIssue(lineno, raw_line, "Key is not uppercase")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(
                    lineno,
                    raw_line,
                    f"Duplicate key (first seen on line {seen_keys[key]})",
                )
            )
        else:
            seen_keys[key] = lineno

        if value.startswith(("'", '"')) and not (
            value.endswith(value[0]) and len(value) > 1
        ):
            result.issues.append(
                LintIssue(lineno, raw_line, "Unmatched quote in value")
            )

    return result
