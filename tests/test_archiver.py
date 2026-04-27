"""Tests for envdiff.archiver."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from envdiff.archiver import ArchiveResult, RestoreResult, archive, restore


@pytest.fixture()
def env_dir(tmp_path: Path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY_A=alpha\nSECRET=s3cr3t\n")
    b.write_text("KEY_B=beta\n")
    return tmp_path, a, b


def test_archive_creates_zip(env_dir, tmp_path):
    _, a, b = env_dir
    out = tmp_path / "bundle.zip"
    result = archive([str(a), str(b)], str(out))
    assert result.ok
    assert out.exists()


def test_archive_result_lists_files(env_dir, tmp_path):
    _, a, b = env_dir
    out = tmp_path / "bundle.zip"
    result = archive([str(a), str(b)], str(out))
    assert set(result.files) == {"a.env", "b.env"}


def test_archive_contains_meta(env_dir, tmp_path):
    _, a, b = env_dir
    out = tmp_path / "bundle.zip"
    archive([str(a), str(b)], str(out), label="prod")
    with zipfile.ZipFile(out) as zf:
        meta = json.loads(zf.read("_meta.json"))
    assert meta["label"] == "prod"
    assert set(meta["files"]) == {"a.env", "b.env"}


def test_archive_missing_file_returns_error(tmp_path):
    out = tmp_path / "bundle.zip"
    result = archive([str(tmp_path / "ghost.env")], str(out))
    assert not result.ok
    assert "ghost.env" in result.error


def test_restore_extracts_files(env_dir, tmp_path):
    _, a, b = env_dir
    out = tmp_path / "bundle.zip"
    archive([str(a), str(b)], str(out))
    dest = tmp_path / "restored"
    result = restore(str(out), str(dest))
    assert result.ok
    assert (dest / "a.env").exists()
    assert (dest / "b.env").exists()


def test_restore_content_matches_original(env_dir, tmp_path):
    _, a, _ = env_dir
    out = tmp_path / "bundle.zip"
    archive([str(a)], str(out))
    dest = tmp_path / "restored"
    restore(str(out), str(dest))
    assert (dest / "a.env").read_text() == a.read_text()


def test_restore_bad_archive_returns_error(tmp_path):
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"not a zip")
    result = restore(str(bad), str(tmp_path / "dest"))
    assert not result.ok


def test_summary_ok(env_dir, tmp_path):
    _, a, _ = env_dir
    out = tmp_path / "bundle.zip"
    result = archive([str(a)], str(out))
    assert "a.env" in result.summary()
    assert "1 file" in result.summary()


def test_restore_summary_ok(env_dir, tmp_path):
    _, a, _ = env_dir
    out = tmp_path / "bundle.zip"
    archive([str(a)], str(out))
    dest = tmp_path / "out"
    result = restore(str(out), str(dest))
    assert str(dest) in result.summary()
