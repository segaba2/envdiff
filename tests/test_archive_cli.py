"""Tests for envdiff.archive_cli."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from envdiff.archive_cli import run


@pytest.fixture()
def env_dir(tmp_path: Path):
    a = tmp_path / "app.env"
    a.write_text("APP_KEY=value\n")
    return tmp_path, a


def _run(*args: str) -> int:
    return run(list(args))


def test_pack_exit_zero(env_dir, tmp_path):
    _, a = env_dir
    out = tmp_path / "out.zip"
    code = _run("pack", str(a), "-o", str(out))
    assert code == 0


def test_pack_creates_file(env_dir, tmp_path):
    _, a = env_dir
    out = tmp_path / "out.zip"
    _run("pack", str(a), "-o", str(out))
    assert out.exists()


def test_pack_missing_file_exits_one(tmp_path):
    out = tmp_path / "out.zip"
    code = _run("pack", str(tmp_path / "nope.env"), "-o", str(out))
    assert code == 1


def test_unpack_exit_zero(env_dir, tmp_path):
    _, a = env_dir
    out = tmp_path / "out.zip"
    _run("pack", str(a), "-o", str(out))
    dest = tmp_path / "restored"
    code = _run("unpack", str(out), "-d", str(dest))
    assert code == 0


def test_unpack_restores_env_file(env_dir, tmp_path):
    _, a = env_dir
    out = tmp_path / "out.zip"
    _run("pack", str(a), "-o", str(out))
    dest = tmp_path / "restored"
    _run("unpack", str(out), "-d", str(dest))
    assert (dest / "app.env").read_text() == a.read_text()


def test_unpack_bad_archive_exits_one(tmp_path):
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"garbage")
    code = _run("unpack", str(bad), "-d", str(tmp_path / "out"))
    assert code == 1


def test_pack_with_label(env_dir, tmp_path):
    import json
    _, a = env_dir
    out = tmp_path / "out.zip"
    _run("pack", str(a), "-o", str(out), "--label", "staging")
    with zipfile.ZipFile(out) as zf:
        meta = json.loads(zf.read("_meta.json"))
    assert meta["label"] == "staging"
