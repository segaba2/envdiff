"""Tests for envdiff.promote_cli."""
from __future__ import annotations

import json
import pathlib

import pytest

from envdiff.promote_cli import run


@pytest.fixture
def env_dir(tmp_path: pathlib.Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def _run(args):
    return run(args)


def test_exit_zero_no_conflicts(env_dir):
    src = env_dir("src.env", "NEW_KEY=hello\n")
    dst = env_dir("dst.env", "APP_ENV=staging\n")
    assert _run([src, dst]) == 0


def test_exit_one_on_conflict(env_dir):
    src = env_dir("src.env", "DB_HOST=prod\n")
    dst = env_dir("dst.env", "DB_HOST=localhost\n")
    assert _run([src, dst]) == 1


def test_exit_zero_with_overwrite_even_on_conflict(env_dir):
    src = env_dir("src.env", "DB_HOST=prod\n")
    dst = env_dir("dst.env", "DB_HOST=localhost\n")
    assert _run([src, dst, "--overwrite"]) == 0


def test_json_output_is_valid(env_dir, capsys):
    src = env_dir("src.env", "NEW=1\nDB_HOST=prod\n")
    dst = env_dir("dst.env", "DB_HOST=localhost\n")
    _run([src, dst, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "promoted" in data
    assert "conflicts" in data
    assert "summary" in data


def test_json_conflict_structure(env_dir, capsys):
    src = env_dir("src.env", "DB_HOST=prod\n")
    dst = env_dir("dst.env", "DB_HOST=localhost\n")
    _run([src, dst, "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data["conflicts"]["DB_HOST"]["source"] == "prod"
    assert data["conflicts"]["DB_HOST"]["destination"] == "localhost"


def test_specific_keys_only(env_dir, capsys):
    src = env_dir("src.env", "A=1\nB=2\n")
    dst = env_dir("dst.env", "")
    _run([src, dst, "--keys", "A", "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert "A" in data["promoted"]
    assert "B" not in data["promoted"]


def test_exit_one_on_missing_file(env_dir):
    dst = env_dir("dst.env", "A=1\n")
    assert _run(["/no/such/file.env", dst]) == 1


def test_text_output_shows_summary(env_dir, capsys):
    src = env_dir("src.env", "ONLY_IN_SRC=yes\n")
    dst = env_dir("dst.env", "")
    _run([src, dst, "--format", "text"])
    out = capsys.readouterr().out
    assert "promoted" in out
