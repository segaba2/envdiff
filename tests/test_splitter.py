"""Tests for envdiff.splitter."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.splitter import split, split_to_files, SplitResult


@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
    }


def test_split_groups_by_prefix(sample_env):
    result = split(sample_env)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_split_ungrouped_single_segment(sample_env):
    result = split(sample_env)
    assert "PORT" in result.ungrouped


def test_split_group_contents_correct(sample_env):
    result = split(sample_env)
    assert result.groups["DB"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_split_explicit_prefixes_filters(sample_env):
    result = split(sample_env, prefixes=["DB"])
    assert "DB" in result.groups
    assert "AWS" not in result.groups
    assert "AWS_KEY" in result.ungrouped


def test_split_min_group_size_moves_small_groups():
    env = {"DB_HOST": "localhost", "AWS_KEY": "abc", "AWS_SECRET": "xyz"}
    result = split(env, min_group_size=2)
    assert "AWS" in result.groups
    assert "DB" not in result.groups
    assert "DB_HOST" in result.ungrouped


def test_split_summary_string(sample_env):
    result = split(sample_env)
    s = result.summary()
    assert "group" in s


def test_split_to_files_creates_files(tmp_path, sample_env):
    source = tmp_path / "test.env"
    source.write_text(
        "\n".join(f"{k}={v}" for k, v in sample_env.items()) + "\n"
    )
    out_dir = tmp_path / "split"
    result = split_to_files(source, out_dir)
    assert out_dir.exists()
    assert len(result.output_files) >= 2


def test_split_to_files_group_file_content(tmp_path, sample_env):
    source = tmp_path / "test.env"
    source.write_text(
        "\n".join(f"{k}={v}" for k, v in sample_env.items()) + "\n"
    )
    out_dir = tmp_path / "split"
    split_to_files(source, out_dir)
    db_file = out_dir / "db.env"
    assert db_file.exists()
    content = db_file.read_text()
    assert "DB_HOST=localhost" in content


def test_split_to_files_ungrouped_written(tmp_path, sample_env):
    source = tmp_path / "test.env"
    source.write_text(
        "\n".join(f"{k}={v}" for k, v in sample_env.items()) + "\n"
    )
    out_dir = tmp_path / "split"
    split_to_files(source, out_dir)
    ungrouped_file = out_dir / "ungrouped.env"
    assert ungrouped_file.exists()
    assert "PORT=8080" in ungrouped_file.read_text()


def test_split_to_files_no_ungrouped_when_disabled(tmp_path, sample_env):
    source = tmp_path / "test.env"
    source.write_text(
        "\n".join(f"{k}={v}" for k, v in sample_env.items()) + "\n"
    )
    out_dir = tmp_path / "split"
    result = split_to_files(source, out_dir, include_ungrouped=False)
    assert not (out_dir / "ungrouped.env").exists()
