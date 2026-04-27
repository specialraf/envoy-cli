"""Tests for envoy.pin and envoy.cli_pin."""

import pytest
from click.testing import CliRunner

from envoy.pin import pin_project, unpin_project, get_pin, list_pins
from envoy.cli_pin import pin_cmd


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    monkeypatch.setattr("envoy.config._get_config_path", lambda: cfg_file)
    monkeypatch.setattr("envoy.pin.load_config", __import__("envoy.config", fromlist=["load_config"]).load_config)
    monkeypatch.setattr("envoy.pin.save_config", __import__("envoy.config", fromlist=["save_config"]).save_config)
    yield


@pytest.fixture
def runner():
    return CliRunner()


def test_pin_project_returns_entry():
    entry = pin_project("myapp", "snap-2024-01-01")
    assert entry.project == "myapp"
    assert entry.snapshot == "snap-2024-01-01"
    assert entry.note is None


def test_pin_project_with_note():
    entry = pin_project("myapp", "snap-2024-01-01", note="stable release")
    assert entry.note == "stable release"


def test_get_pin_returns_entry_after_pin():
    pin_project("myapp", "snap-abc")
    entry = get_pin("myapp")
    assert entry is not None
    assert entry.snapshot == "snap-abc"


def test_get_pin_returns_none_when_not_pinned():
    assert get_pin("ghost") is None


def test_unpin_removes_entry():
    pin_project("myapp", "snap-abc")
    unpin_project("myapp")
    assert get_pin("myapp") is None


def test_unpin_missing_raises_key_error():
    with pytest.raises(KeyError, match="not pinned"):
        unpin_project("nonexistent")


def test_list_pins_empty_initially():
    assert list_pins() == []


def test_list_pins_returns_all():
    pin_project("app1", "snap-1")
    pin_project("app2", "snap-2")
    pins = list_pins()
    projects = {p.project for p in pins}
    assert projects == {"app1", "app2"}


def test_cli_set_pin(runner):
    result = runner.invoke(pin_cmd, ["set", "myapp", "snap-xyz"])
    assert result.exit_code == 0
    assert "Pinned" in result.output


def test_cli_set_pin_with_note(runner):
    result = runner.invoke(pin_cmd, ["set", "myapp", "snap-xyz", "--note", "prod freeze"])
    assert result.exit_code == 0
    assert "prod freeze" in result.output


def test_cli_remove_pin(runner):
    pin_project("myapp", "snap-xyz")
    result = runner.invoke(pin_cmd, ["remove", "myapp"])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_cli_remove_pin_not_found(runner):
    result = runner.invoke(pin_cmd, ["remove", "ghost"])
    assert result.exit_code != 0


def test_cli_list_empty(runner):
    result = runner.invoke(pin_cmd, ["list"])
    assert result.exit_code == 0
    assert "No projects" in result.output


def test_cli_show_pin(runner):
    pin_project("myapp", "snap-2024")
    result = runner.invoke(pin_cmd, ["show", "myapp"])
    assert result.exit_code == 0
    assert "snap-2024" in result.output
