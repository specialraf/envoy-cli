"""Pin management: lock a project to a specific snapshot for reproducible environments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy.config import get_value, set_value, load_config, save_config

_PINS_KEY = "pins"


@dataclass
class PinEntry:
    project: str
    snapshot: str
    note: Optional[str] = None


def _get_pins() -> dict:
    cfg = load_config()
    return cfg.get(_PINS_KEY, {})


def _save_pins(pins: dict) -> None:
    cfg = load_config()
    cfg[_PINS_KEY] = pins
    save_config(cfg)


def pin_project(project: str, snapshot: str, note: Optional[str] = None) -> PinEntry:
    """Pin a project to a specific snapshot name."""
    pins = _get_pins()
    pins[project] = {"snapshot": snapshot, "note": note}
    _save_pins(pins)
    return PinEntry(project=project, snapshot=snapshot, note=note)


def unpin_project(project: str) -> None:
    """Remove a pin for a project. Raises KeyError if not pinned."""
    pins = _get_pins()
    if project not in pins:
        raise KeyError(f"Project '{project}' is not pinned.")
    del pins[project]
    _save_pins(pins)


def get_pin(project: str) -> Optional[PinEntry]:
    """Return the PinEntry for a project, or None if unpinned."""
    pins = _get_pins()
    entry = pins.get(project)
    if entry is None:
        return None
    return PinEntry(project=project, snapshot=entry["snapshot"], note=entry.get("note"))


def list_pins() -> list[PinEntry]:
    """Return all pinned projects."""
    pins = _get_pins()
    return [
        PinEntry(project=proj, snapshot=data["snapshot"], note=data.get("note"))
        for proj, data in pins.items()
    ]
