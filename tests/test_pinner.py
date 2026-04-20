"""Tests for envdiff.pinner and envdiff.pin_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.pinner import pin, load_pins, PinResult
from envdiff.pin_cli import run


@pytest.fixture()
def env_file(tmp_path: Path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


@pytest.fixture()
def lockfile(tmp_path: Path) -> str:
    return str(tmp_path / ".env.lock")


def test_pin_creates_lockfile(env_file, lockfile):
    path = env_file("FOO=bar\nBAZ=qux\n")
    result = pin(path, lockfile)
    assert Path(lockfile).exists()
    assert result.pinned == {"FOO": "bar", "BAZ": "qux"}


def test_pin_no_changes_on_second_identical_run(env_file, lockfile):
    path = env_file("FOO=bar\n")
    pin(path, lockfile)
    result = pin(path, lockfile)
    assert not result.has_changes()


def test_pin_detects_added_key(env_file, lockfile):
    path = env_file("FOO=bar\n")
    pin(path, lockfile)
    path2 = env_file("FOO=bar\nNEW=value\n")
    result = pin(path2, lockfile)
    assert "NEW" in result.added
    assert result.has_changes()


def test_pin_detects_removed_key(env_file, lockfile):
    path = env_file("FOO=bar\nOLD=gone\n")
    pin(path, lockfile)
    path2 = env_file("FOO=bar\n")
    result = pin(path2, lockfile)
    assert "OLD" in result.removed


def test_pin_detects_changed_value(env_file, lockfile):
    path = env_file("FOO=bar\n")
    pin(path, lockfile)
    path2 = env_file("FOO=newval\n")
    result = pin(path2, lockfile)
    assert "FOO" in result.changed


def test_summary_unchanged(env_file, lockfile):
    path = env_file("A=1\nB=2\n")
    pin(path, lockfile)
    result = pin(path, lockfile)
    assert "unchanged" in result.summary()
    assert "2 keys" in result.summary()


def test_summary_with_changes(env_file, lockfile):
    path = env_file("A=1\n")
    pin(path, lockfile)
    result = pin(env_file("A=2\nB=3\n"), lockfile)
    s = result.summary()
    assert "+1 added" in s
    assert "~1 changed" in s


def test_load_pins_returns_dict(env_file, lockfile):
    path = env_file("X=hello\n")
    pin(path, lockfile)
    pins = load_pins(lockfile)
    assert pins["X"] == "hello"


def test_load_pins_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_pins(str(tmp_path / "missing.lock"))


def test_cli_save_exit_zero_no_changes(env_file, lockfile, tmp_path):
    path = env_file("K=v\n")
    run(["save", path, "--lock", lockfile])
    code = run(["save", path, "--lock", lockfile])
    assert code == 0


def test_cli_save_exit_one_on_changes(env_file, lockfile):
    path = env_file("K=v\n")
    run(["save", path, "--lock", lockfile])
    path2 = env_file("K=v\nNEW=1\n")
    code = run(["save", path2, "--lock", lockfile])
    assert code == 1


def test_cli_show_prints_keys(env_file, lockfile, capsys):
    path = env_file("ALPHA=one\nBETA=two\n")
    run(["save", path, "--lock", lockfile, "--quiet"])
    run(["show", "--lock", lockfile])
    out = capsys.readouterr().out
    assert "ALPHA=one" in out
    assert "BETA=two" in out
