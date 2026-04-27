"""Tests for envdiff.differ_stats and envdiff.stats_cli."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_stats import DiffStats, compute_stats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(missing_a=(), missing_b=(), mismatches=None):
    if mismatches is None:
        mismatches = {}
    return DiffResult(
        missing_in_a=set(missing_a),
        missing_in_b=set(missing_b),
        mismatches=dict(mismatches),
    )


# ---------------------------------------------------------------------------
# Unit tests for compute_stats
# ---------------------------------------------------------------------------

def test_empty_list_returns_zero_stats():
    stats = compute_stats([])
    assert stats.total_pairs == 0
    assert stats.pairs_with_diff == 0
    assert stats.diff_rate == 0.0


def test_clean_pair_counted_correctly():
    stats = compute_stats([_result()])
    assert stats.total_pairs == 1
    assert stats.pairs_clean == 1
    assert stats.pairs_with_diff == 0


def test_dirty_pair_counted_correctly():
    stats = compute_stats([_result(missing_b=["FOO"])])
    assert stats.pairs_with_diff == 1
    assert stats.total_missing_b == 1


def test_diff_rate_calculation():
    results = [_result(missing_a=["X"]), _result(), _result(mismatches={"Y": ("1", "2")})]
    stats = compute_stats(results)
    assert stats.diff_rate == pytest.approx(2 / 3)


def test_totals_accumulate_across_pairs():
    r1 = _result(missing_a=["A", "B"], missing_b=["C"])
    r2 = _result(missing_b=["D"], mismatches={"E": ("v1", "v2")})
    stats = compute_stats([r1, r2])
    assert stats.total_missing_a == 2
    assert stats.total_missing_b == 2
    assert stats.total_mismatches == 1


def test_most_common_missing_ordered():
    r1 = _result(missing_b=["FOO", "BAR"])
    r2 = _result(missing_a=["FOO"])
    stats = compute_stats([r1, r2])
    assert stats.most_common_missing[0] == "FOO"


def test_summary_contains_key_fields():
    stats = compute_stats([_result(missing_b=["X"])])
    text = stats.summary()
    assert "Pairs compared" in text
    assert "Mismatches" in text


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_dir(tmp_path):
    def write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return write


def _run(argv):
    from envdiff.stats_cli import run
    return run(argv)


def test_cli_exit_zero_when_clean(env_dir):
    a = env_dir("a.env", "KEY=val\n")
    b = env_dir("b.env", "KEY=val\n")
    assert _run([a, b]) == 0


def test_cli_exit_one_when_diff(env_dir):
    a = env_dir("a.env", "KEY=val\n")
    b = env_dir("b.env", "OTHER=val\n")
    assert _run([a, b]) == 1


def test_cli_exit_two_on_odd_files(env_dir):
    a = env_dir("a.env", "KEY=val\n")
    assert _run([a]) == 2


def test_cli_json_output_valid(env_dir, capsys):
    a = env_dir("a.env", "KEY=val\n")
    b = env_dir("b.env", "KEY=val\n")
    _run(["--format", "json", a, b])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total_pairs" in data
    assert data["total_pairs"] == 1


def test_cli_multiple_pairs(env_dir, capsys):
    a = env_dir("a.env", "X=1\n")
    b = env_dir("b.env", "X=1\n")
    c = env_dir("c.env", "X=1\nY=2\n")
    d = env_dir("d.env", "X=1\n")
    _run(["--format", "json", a, b, c, d])
    data = json.loads(capsys.readouterr().out)
    assert data["total_pairs"] == 2
