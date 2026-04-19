"""Tests for differ_matrix and matrix_cli."""
import json
import os
import pytest
from pathlib import Path
from envdiff.differ_matrix import diff_matrix
from envdiff.matrix_cli import run


@pytest.fixture()
def env_dir(tmp_path: Path):
    files = {
        "a.env": "KEY1=foo\nKEY2=bar\nSHARED=same\n",
        "b.env": "KEY1=foo\nKEY3=baz\nSHARED=same\n",
        "c.env": "KEY1=different\nSHARED=same\n",
    }
    paths = {}
    for name, content in files.items():
        p = tmp_path / name
        p.write_text(content)
        paths[name] = str(p)
    return paths


def test_matrix_has_correct_pairs(env_dir):
    paths = list(env_dir.values())
    result = diff_matrix(paths)
    assert len(result.cells) == 3  # (0,1),(0,2),(1,2)


def test_any_diff_true_when_mismatch(env_dir):
    result = diff_matrix(list(env_dir.values()))
    assert result.any_diff()


def test_no_diff_identical_files(tmp_path):
    content = "A=1\nB=2\n"
    f1 = tmp_path / "x.env"
    f2 = tmp_path / "y.env"
    f1.write_text(content)
    f2.write_text(content)
    result = diff_matrix([str(f1), str(f2)])
    assert not result.any_diff()
    assert result.pairs_with_diff() == []


def test_summary_string(env_dir):
    result = diff_matrix(list(env_dir.values()))
    s = result.summary()
    assert "pairs" in s


def test_cli_exit_nonzero_on_diff(env_dir):
    code = run(list(env_dir.values()))
    assert code == 1


def test_cli_exit_zero_on_identical(tmp_path):
    content = "X=1\n"
    f1 = tmp_path / "p.env"
    f2 = tmp_path / "q.env"
    f1.write_text(content)
    f2.write_text(content)
    assert run([str(f1), str(f2)]) == 0


def test_cli_json_output_valid(env_dir, capsys):
    run(["--format", "json"] + list(env_dir.values()))
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "pairs" in data
    assert isinstance(data["pairs"], list)


def test_cli_requires_two_files(tmp_path):
    f = tmp_path / "only.env"
    f.write_text("A=1\n")
    assert run([str(f)]) == 2
