"""Audit log for tracking .env access and sync events."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILENAME = "audit.log"


def _get_audit_log_path() -> Path:
    """Return the path to the audit log file."""
    base = Path(os.environ.get("ENVOY_HOME", Path.home() / ".envoy"))
    base.mkdir(parents=True, exist_ok=True)
    return base / AUDIT_LOG_FILENAME


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def record(
    action: str,
    project: str,
    user: Optional[str] = None,
    details: Optional[str] = None,
) -> dict:
    """Append an audit entry and return the recorded entry."""
    entry = {
        "timestamp": _now_iso(),
        "action": action,
        "project": project,
        "user": user or os.environ.get("USER", "unknown"),
        "details": details,
    }
    log_path = _get_audit_log_path()
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def read_log(limit: int = 50) -> list[dict]:
    """Read the most recent *limit* audit entries (oldest first)."""
    log_path = _get_audit_log_path()
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries[-limit:]


def clear_log() -> None:
    """Remove all audit log entries."""
    log_path = _get_audit_log_path()
    if log_path.exists():
        log_path.unlink()
