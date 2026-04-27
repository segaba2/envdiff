"""Tests for envdiff.tracer."""
from pathlib import Path

import pytest

from envdiff.tracer import trace, TraceResult


@pytest.fixture()
def env_dir(tmp_path: Path):
    base = tmp_path / "base.env"
    override = tmp_path / "override.env"
    extra = tmp_path / "extra.env"
    base.write_text("HOST=localhost\nPORT=5432\nDEBUG=false\n")
    override.write_text("HOST=prod.example.com\nDEBUG=true\n")
    extra.write_text("NEW_KEY=hello\n")
    return base, override, extra


def test_trace_returns_trace_result(env_dir):
    base, override, _ = env_dir
    result = trace([str(base), str(override)])
    assert isinstance(result, TraceResult)


def test_all_keys_union(env_dir):
    base, override, extra = env_dir
    result = trace([str(base), str(override), str(extra)])
    assert set(result.all_keys()) == {"HOST", "PORT", "DEBUG", "NEW_KEY"}


def test_winning_entry_is_last_file(env_dir):
    base, override, _ = env_dir
    result = trace([str(base), str(override)])
    winner = result.winning_entry("HOST")
    assert winner is not None
    assert winner.value == "prod.example.com"
    assert "override.env" in winner.source


def test_sources_for_tracks_all_files(env_dir):
    base, override, _ = env_dir
    result = trace([str(base), str(override)])
    sources = result.sources_for("HOST")
    assert len(sources) == 2
    assert any("base.env" in s for s in sources)
    assert any("override.env" in s for s in sources)


def test_key_defined_once_has_single_source(env_dir):
    base, override, _ = env_dir
    result = trace([str(base), str(override)])
    sources = result.sources_for("PORT")
    assert len(sources) == 1


def test_winning_entry_none_for_missing_key(env_dir):
    base, _, _ = env_dir
    result = trace([str(base)])
    assert result.winning_entry("NONEXISTENT") is None


def test_summary_contains_conflict_tag(env_dir):
    base, override, _ = env_dir
    result = trace([str(base), str(override)])
    summary = result.summary()
    assert "[conflict]" in summary


def test_summary_no_conflict_when_values_same(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=same\n")
    b.write_text("KEY=same\n")
    result = trace([str(a), str(b)])
    assert "[conflict]" not in result.summary()


def test_empty_file_list_returns_empty_result():
    result = trace([])
    assert result.all_keys() == []
    assert result.summary() == "(no keys traced)"
