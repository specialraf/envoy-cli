"""Pre/post hooks for envoy operations (push, pull, set, get)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from envoy.config import get_value, set_value

HOOK_KEYS = {
    "pre_push",
    "post_push",
    "pre_pull",
    "post_pull",
    "pre_set",
    "post_set",
}


@dataclass
class HookResult:
    hook: str
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _validate_hook_name(name: str) -> None:
    """Raise ValueError if *name* is not a recognised hook key."""
    if name not in HOOK_KEYS:
        raise ValueError(f"Unknown hook '{name}'. Valid hooks: {sorted(HOOK_KEYS)}")


def get_hook(name: str) -> Optional[str]:
    """Return the shell command registered for *name*, or None."""
    _validate_hook_name(name)
    value = get_value(f"hook_{name}")
    return value if value else None


def set_hook(name: str, command: str) -> None:
    """Register *command* as the shell command for hook *name*."""
    _validate_hook_name(name)
    set_value(f"hook_{name}", command)


def clear_hook(name: str) -> None:
    """Remove the registered command for hook *name*."""
    _validate_hook_name(name)
    set_value(f"hook_{name}", "")


def run_hook(name: str, env: Optional[dict] = None) -> Optional[HookResult]:
    """Run the hook *name* if one is registered. Returns HookResult or None."""
    command = get_hook(name)
    if not command:
        return None
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return HookResult(
        hook=name,
        command=command,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def list_hooks() -> List[dict]:
    """Return all hooks with their registered commands (empty string if unset)."""
    hooks = []
    for name in sorted(HOOK_KEYS):
        cmd = get_value(f"hook_{name}") or ""
        hooks.append({"hook": name, "command": cmd})
    return hooks
