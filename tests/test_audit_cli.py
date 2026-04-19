"""Tests for envdiff.audit_cli."""
import json
from pathlib import Path

import pytest

from envdiff.audit_cli import build_parser, run


@pytest.fixture
def env_pair(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=1\nBAR=2\n")
    b.write_text("FOO=1\nBAZ=3\n")
    return a, b


def _run(args_list):
    parser = build_parser()
    return run(parser.parse_args(args_list))


def test_exitzero_on_diff(env_pair, tmp_path):
    a, b = env_pair
    log = tmp_path / "log.json"
    code(a), str(b), "--log", str(log)])
    assert code == 1


def test_exit_code_zero_on_no_diff(tmp_path):
    a = tmp_path / "a.envpath / "b.env"
    a.write_text("FOO=1\n")
    b.write_text("FOO=1\n")
    log = tmp_path / "log.json"
    code = _run([str(a), str(b), "--log", str(log)])
    assert code == 0


def test_log_file_created(env_pair, tmp_path):
    a, b = env_pair
    log = tmp_path / "audit.json"
    _run([str(a), str(b), "--log", str(log)])
    assert log.exists()


def test_log_contains_entry(env_pair, tmp_path):
    a, b = env_pair
    log = tmp_path / "audit.json"
    _run([str(a), str(b), "--log", str(log), "--tag", "test"])
    data = json.loads(log.read_text())
    assert len(data["entries"]) == 1
    assert data["entries"][0]["tag"] == "test"


def test_log_accumulates_entries(env_pair, tmp_path):
    a, b = env_pair
    log = tmp_path / "audit.json"
    _run([str(a), str(b), "--log", str(log)])
    _run([str(a), str(b), "--log", str(log)])
    data = json.loads(log.read_text())
    assert len(data["entries"]) == 2


def test_bad_file_returns_error(tmp_path):
    log = tmp_path / "audit.json"
    code = _run(["nonexistent_a.env", "nonexistent_b.env", "--log", str(log)])
    assert code == 1
