"""Tests for differ_graph and graph_cli."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envdiff.differ_graph import build_graph, GraphResult, GraphEdge
from envdiff.graph_cli import run


@pytest.fixture()
def env_dir(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_build_graph_returns_graph_result(env_dir):
    a = env_dir("a.env", "FOO=1\nBAR=2\n")
    b = env_dir("b.env", "FOO=1\nBAR=2\n")
    result = build_graph([a, b])
    assert isinstance(result, GraphResult)


def test_no_diff_identical_files(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=1\n")
    result = build_graph([a, b])
    assert not result.any_diff()


def test_mismatch_detected(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=2\n")
    result = build_graph([a, b])
    assert result.any_diff()
    assert "FOO" in result.edges[0].mismatches


def test_missing_key_detected(env_dir):
    a = env_dir("a.env", "FOO=1\nBAR=2\n")
    b = env_dir("b.env", "FOO=1\n")
    result = build_graph([a, b])
    assert "BAR" in result.edges[0].missing_in_b


def test_three_files_correct_edge_count(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=1\n")
    c = env_dir("c.env", "FOO=1\n")
    result = build_graph([a, b, c])
    assert len(result.edges) == 3  # C(3,2)


def test_isolated_files_no_diff(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=1\n")
    result = build_graph([a, b])
    isolated = result.isolated_files()
    assert a in isolated and b in isolated


def test_isolated_files_excludes_differing(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=2\n")
    result = build_graph([a, b])
    assert result.isolated_files() == []


def test_summary_string(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=2\n")
    result = build_graph([a, b])
    s = result.summary()
    assert "2 files" in s
    assert "1 pairs" in s


def test_cli_exit_zero_no_diff(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=1\n")
    assert run([a, b]) == 0


def test_cli_exit_one_on_diff(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=2\n")
    assert run([a, b]) == 1


def test_cli_json_output(env_dir, capsys):
    a = env_dir("a.env", "FOO=1\n")
    b = env_dir("b.env", "FOO=1\n")
    run([a, b, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "edges" in data
    assert "summary" in data


def test_cli_missing_file_exits_one(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    assert run([a, "/nonexistent/x.env"]) == 1


def test_cli_single_file_exits_one(env_dir):
    a = env_dir("a.env", "FOO=1\n")
    assert run([a]) == 1
