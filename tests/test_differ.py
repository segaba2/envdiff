"""Tests for envdiff.differ — integration of parse/filter/sort/compare."""
import pytest
from pathlib import Path

from envdiff.differ import diff_files


@pytest.fixture()
def env_files(tmp_path: Path):
    """Write two .env files and return their paths."""
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(
        "APP_NAME=myapp\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "SECRET_KEY=abc123\n"
        "DEBUG=true\n"
    )
    b.write_text(
        "APP_NAME=myapp\n"
        "DB_HOST=prod.db\n"
        "DB_PORT=5432\n"
        "API_KEY=xyz\n"
    )
    return str(a), str(b)


def test_basic_diff(env_files):
    a, b = env_files
    result = diff_files(a, b)
    assert "SECRET_KEY" in result.missing_in_b
    assert "DEBUG" in result.missing_in_b
    assert "API_KEY" in result.missing_in_a
    assert "DB_HOST" in result.mismatched


def test_no_diff_same_files(tmp_path):
    f = tmp_path / "same.env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    result = diff_files(str(f), str(f))
    assert not result.missing_in_a
    assert not result.missing_in_b
    assert not result.mismatched


def test_exclude_patterns(env_files):
    a, b = env_files
    result = diff_files(a, b, exclude_patterns=["SECRET_*", "DEBUG"])
    assert "SECRET_KEY" not in result.missing_in_b
    assert "DEBUG" not in result.missing_in_b


def test_prefix_filter(env_files):
    a, b = env_files
    result = diff_files(a, b, prefix="DB_")
    # Only DB_* keys survive; DB_HOST is a mismatch, DB_PORT matches
    assert "DB_HOST" in result.mismatched
    assert "APP_NAME" not in result.mismatched
    assert "SECRET_KEY" not in result.missing_in_b


def test_sort_alpha(env_files):
    a, b = env_files
    result = diff_files(a, b, sort="alpha")
    # Result object exists and has the expected attributes
    assert hasattr(result, "missing_in_a")
    assert hasattr(result, "missing_in_b")
    assert hasattr(result, "mismatched")


def test_missing_file_raises(tmp_path):
    real = tmp_path / "real.env"
    real.write_text("K=V\n")
    with pytest.raises(FileNotFoundError):
        diff_files(str(real), str(tmp_path / "ghost.env"))
