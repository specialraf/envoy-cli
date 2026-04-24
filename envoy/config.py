"""User-level configuration management for envoy-cli."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "envoy" / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "remote_url": "",
    "default_project": "",
    "token": "",
    "timeout": 10,
}


def _get_config_path() -> Path:
    """Return config path, allowing override via env var."""
    env_path = os.environ.get("ENVOY_CONFIG_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_CONFIG_PATH


def load_config() -> Dict[str, Any]:
    """Load config from disk, returning defaults for missing keys."""
    path = _get_config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with path.open("r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)
    # Merge with defaults so new keys are always present
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def save_config(config: Dict[str, Any]) -> None:
    """Persist config dict to disk."""
    path = _get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(config, f, indent=2)


def get_value(key: str) -> Optional[Any]:
    """Retrieve a single config value by key."""
    return load_config().get(key)


def set_value(key: str, value: Any) -> None:
    """Set a single config value and persist."""
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"Unknown config key: {key!r}")
    config = load_config()
    config[key] = value
    save_config(config)
