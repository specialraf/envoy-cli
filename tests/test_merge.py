"""Tests for envoy.merge."""
import pytest

from envoy.storage import save_env
from envoy.merge import merge_projects, merge_file, MergeResult


PASSWORD = "test-secret"


@pytest.fixture()
def store(tmp_path):
    """Return a helper that saves an env and returns the store path."""
    def _save(project: str, content: str) -> str:
        save_env(project, content, PASSWORD, store_path=str(tmp_path))
        return str(tmp_path)
    return _save


def test_merge_projects_adds_new_keys(store):
    sp = store("base", "A=1\nB=2")
    store("overlay", "C=3")
    result = merge_projects("base", "overlay", PASSWORD, store_path=sp)
    assert "C" in result.added
    assert result.final_env["C"] == "3"


def test_merge_projects_skips_existing_by_default(store):
    sp = store("base", "A=1\nB=2")
    store("overlay", "A=99\nC=3")
    result = merge_projects("base", "overlay", PASSWORD, store_path=sp)
    assert "A" in result.skipped
    assert result.final_env["A"] == "1"  # unchanged


def test_merge_projects_overwrites_when_flag_set(store):
    sp = store("base", "A=1\nB=2")
    store("overlay", "A=99")
    result = merge_projects("base", "overlay", PASSWORD, overwrite=True, store_path=sp)
    assert "A" in result.updated
    assert result.final_env["A"] == "99"


def test_merge_projects_preserves_base_only_keys(store):
    sp = store("base", "A=1\nB=2")
    store("overlay", "C=3")
    result = merge_projects("base", "overlay", PASSWORD, store_path=sp)
    assert result.final_env["A"] == "1"
    assert result.final_env["B"] == "2"


def test_merge_projects_persists_to_storage(store, tmp_path):
    sp = store("base", "A=1")
    store("overlay", "B=2")
    merge_projects("base", "overlay", PASSWORD, store_path=sp)
    from envoy.storage import load_env
    text = load_env("base", PASSWORD, store_path=sp)
    assert "B=2" in text


def test_merge_file_adds_keys(store):
    sp = store("base", "X=10")
    result = merge_file("base", "Y=20\nZ=30", PASSWORD, store_path=sp)
    assert set(result.added) == {"Y", "Z"}
    assert result.final_env["X"] == "10"


def test_merge_file_skips_comments(store):
    sp = store("base", "A=1")
    result = merge_file("base", "# comment\nB=2", PASSWORD, store_path=sp)
    assert "B" in result.added
    assert len(result.added) == 1


def test_merge_file_overwrite_false_keeps_original(store):
    sp = store("base", "A=original")
    result = merge_file("base", "A=new", PASSWORD, overwrite=False, store_path=sp)
    assert "A" in result.skipped
    assert result.final_env["A"] == "original"


def test_merge_file_overwrite_true_updates_value(store):
    sp = store("base", "A=original")
    result = merge_file("base", "A=new", PASSWORD, overwrite=True, store_path=sp)
    assert "A" in result.updated
    assert result.final_env["A"] == "new"


def test_merge_result_is_dataclass():
    r = MergeResult()
    assert r.added == []
    assert r.updated == []
    assert r.skipped == []
    assert r.final_env == {}
