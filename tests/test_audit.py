"""Tests for envoy.audit module."""

import json
import pytest
from pathlib import Path

from envoy import audit


@pytest.fixture(autouse=True)
def isolated_audit(tmp_path, monkeypatch):
    """Redirect audit log to a temporary directory."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    yield tmp_path


def test_record_returns_entry():
    entry = audit.record("get", "my-project")
    assert entry["action"] == "get"
    assert entry["project"] == "my-project"
    assert "timestamp" in entry


def test_record_writes_to_log(isolated_audit):
    audit.record("set", "alpha", details="added DB_URL")
    log_path = isolated_audit / "audit.log"
    assert log_path.exists()
    line = log_path.read_text().strip()
    data = json.loads(line)
    assert data["action"] == "set"
    assert data["details"] == "added DB_URL"


def test_multiple_records_appended(isolated_audit):
    audit.record("get", "proj-a")
    audit.record("push", "proj-b")
    audit.record("pull", "proj-c")
    entries = audit.read_log()
    assert len(entries) == 3
    assert entries[0]["project"] == "proj-a"
    assert entries[2]["action"] == "pull"


def test_read_log_empty_when_no_file():
    entries = audit.read_log()
    assert entries == []


def test_read_log_respects_limit(isolated_audit):
    for i in range(10):
        audit.record("get", f"project-{i}")
    entries = audit.read_log(limit=3)
    assert len(entries) == 3
    assert entries[-1]["project"] == "project-9"


def test_clear_log_removes_file(isolated_audit):
    audit.record("get", "some-project")
    audit.clear_log()
    assert not (isolated_audit / "audit.log").exists()
    assert audit.read_log() == []


def test_record_uses_env_user(monkeypatch):
    monkeypatch.setenv("USER", "alice")
    entry = audit.record("set", "proj", user=None)
    assert entry["user"] == "alice"


def test_record_explicit_user_overrides_env(monkeypatch):
    monkeypatch.setenv("USER", "alice")
    entry = audit.record("set", "proj", user="bob")
    assert entry["user"] == "bob"
