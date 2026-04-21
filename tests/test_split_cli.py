"""Tests for envdiff.split_cli."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.split_cli import run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "AWS_KEY=abc\n"
        "AWS_SECRET=xyz\n"
        "PORT=8080\n"
    )
    return f


def _run(args: list[str]) -> int:
    return run(args)


def test_exit_zero_on_valid_file(env_file, tmp_path):
    out = tmp_path / "out"
    code = _run([str(env_file), str(out)])
    assert code == 0


def test_exit_one_on_missing_file(tmp_path):
    out = tmp_path / "out"
    code = _run([str(tmp_path / "missing.env"), str(out)])
    assert code == 1


def test_output_dir_created(env_file, tmp_path):
    out = tmp_path / "nested" / "out"
    _run([str(env_file), str(out)])
    assert out.exists()


def test_group_files_written(env_file, tmp_path):
    out = tmp_path / "out"
    _run([str(env_file), str(out)])
    assert (out / "db.env").exists()
    assert (out / "aws.env").exists()


def test_ungrouped_file_written(env_file, tmp_path):
    out = tmp_path / "out"
    _run([str(env_file), str(out)])
    assert (out / "ungrouped.env").exists()


def test_no_ungrouped_flag(env_file, tmp_path):
    out = tmp_path / "out"
    _run([str(env_file), str(out), "--no-ungrouped"])
    assert not (out / "ungrouped.env").exists()


def test_prefix_filter(env_file, tmp_path):
    out = tmp_path / "out"
    _run([str(env_file), str(out), "--prefixes", "DB"])
    assert (out / "db.env").exists()
    assert not (out / "aws.env").exists()


def test_min_group_size(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nAWS_KEY=abc\nAWS_SECRET=xyz\n")
    out = tmp_path / "out"
    _run([str(f), str(out), "--min-group-size", "2"])
    assert (out / "aws.env").exists()
    # DB has only 1 key, should be in ungrouped
    ungrouped = (out / "ungrouped.env").read_text()
    assert "DB_HOST" in ungrouped
