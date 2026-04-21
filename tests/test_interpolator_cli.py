"""Tests for envdiff.interpolator_cli."""

import json
import os
import pytest

from envdiff.interpolator_cli import run


@pytest.fixture
def env_file(tmp_path):
    def _write(content: str):
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def _run(args):
    return run(args)


def test_exit_zero_on_valid_file(env_file):
    path = env_file("BASE=/home\nDIR=$BASE/data\n")
    assert _run([path]) == 0


def test_exit_one_on_missing_file():
    assert _run(["/nonexistent/.env"]) == 1


def test_text_output_shows_expanded_value(env_file, capsys):
    path = env_file("BASE=/srv\nAPP_DIR=$BASE/app\n")
    _run([path])
    out = capsys.readouterr().out
    assert "APP_DIR=/srv/app" in out


def test_text_output_marks_unresolved(env_file, capsys):
    path = env_file("FOO=$MISSING/x\n")
    _run([path])
    out = capsys.readouterr().out
    assert "UNRESOLVED" in out


def test_json_output_is_valid(env_file, capsys):
    path = env_file("A=1\nB=$A\n")
    _run([path, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "env" in data
    assert "resolved" in data
    assert "unresolved" in data


def test_strict_exits_nonzero_on_unresolved(env_file):
    path = env_file("FOO=$GHOST\n")
    assert _run([path, "--strict"]) == 1


def test_strict_exits_zero_when_all_resolved(env_file):
    path = env_file("A=hello\nB=$A\n")
    assert _run([path, "--strict"]) == 0
