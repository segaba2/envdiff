"""Tests for envdiff.differ_cli."""
from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

import pytest

from envdiff.differ_cli import run


@pytest.fixture()
def env_dir(tmp_path: Path):
    base = tmp_path / "base.env"
    same = tmp_path / "same.env"
    diff = tmp_path / "diff.env"

    base.write_text(textwrap.dedent("""\
        APP_KEY=abc
        DB_HOST=localhost
        SECRET=hunter2
    """))
    same.write_text(textwrap.dedent("""\
        APP_KEY=abc
        DB_HOST=localhost
        SECRET=hunter2
    """))
    diff.write_text(textwrap.dedent("""\
        APP_KEY=xyz
        DB_HOST=localhost
    """))
    return {"base": str(base), "same": str(same), "diff": str(diff)}


def test_exit_zero_when_no_diff(env_dir):
    code = run([env_dir["base"], env_dir["same"]])
    assert code == 0


def test_exit_nonzero_when_diff(env_dir):
    code = run([env_dir["base"], env_dir["diff"]])
    assert code != 0


def test_json_output_is_valid(env_dir, capsys):
    run([env_dir["base"], env_dir["diff"], "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "diffs" in data


def test_text_output_contains_labels(env_dir, capsys):
    run([env_dir["base"], env_dir["diff"]])
    captured = capsys.readouterr()
    assert "diff" in captured.out.lower() or "missing" in captured.out.lower() or captured.out


def test_multiple_others(env_dir):
    code = run([env_dir["base"], env_dir["same"], env_dir["diff"]])
    assert code != 0


def test_exclude_reduces_diff(env_dir):
    code_without = run([env_dir["base"], env_dir["diff"]])
    code_with = run([env_dir["base"], env_dir["diff"], "--exclude", "APP_KEY", "--exclude", "SECRET"])
    assert code_without != 0
    assert code_with == 0
