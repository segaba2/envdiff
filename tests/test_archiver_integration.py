"""Integration tests: parse → archive → restore → re-parse roundtrip."""

from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.archiver import archive, restore
from envdiff.parser import parse_env_file


@pytest.fixture()
def env_file(tmp_path: Path):
    p = tmp_path / "prod.env"
    p.write_text(
        'DB_HOST=db.example.com\n'
        'DB_PORT=5432\n'
        'SECRET_KEY=supersecret\n'
        'DEBUG=false\n'
    )
    return p


def test_roundtrip_values_preserved(env_file, tmp_path):
    original = parse_env_file(str(env_file))
    bundle = tmp_path / "bundle.zip"
    archive([str(env_file)], str(bundle))
    dest = tmp_path / "restored"
    restore(str(bundle), str(dest))
    restored = parse_env_file(str(dest / env_file.name))
    assert restored == original


def test_roundtrip_key_count(env_file, tmp_path):
    original = parse_env_file(str(env_file))
    bundle = tmp_path / "bundle.zip"
    archive([str(env_file)], str(bundle))
    dest = tmp_path / "restored"
    restore(str(bundle), str(dest))
    restored = parse_env_file(str(dest / env_file.name))
    assert len(restored) == len(original)


def test_multi_file_roundtrip(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY_A=1\n")
    b.write_text("KEY_B=2\n")
    bundle = tmp_path / "multi.zip"
    archive([str(a), str(b)], str(bundle))
    dest = tmp_path / "out"
    restore(str(bundle), str(dest))
    assert parse_env_file(str(dest / "a.env")) == {"KEY_A": "1"}
    assert parse_env_file(str(dest / "b.env")) == {"KEY_B": "2"}


def test_archive_error_does_not_create_zip(tmp_path):
    bundle = tmp_path / "bundle.zip"
    result = archive([str(tmp_path / "missing.env")], str(bundle))
    assert not result.ok
    assert not bundle.exists()
