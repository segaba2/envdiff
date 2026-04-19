"""Tests for envdiff.differ_plus multi-file diff."""
import os
import pytest
from envdiff.differ_plus import diff_many, MultiDiffResult


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    base.write_text("KEY1=val1\nKEY2=val2\n")
    a.write_text("KEY1=val1\nKEY2=different\n")
    b.write_text("KEY1=val1\n")
    return str(base), str(a), str(b)


def test_diff_many_returns_multi_result(env_files):
    base, a, b = env_files
    result = diff_many(base, [a, b])
    assert isinstance(result, MultiDiffResult)
    assert len(result.pairs) == 2


def test_any_diff_true_when_mismatch(env_files):
    base, a, b = env_files
    result = diff_many(base, [a])
    assert result.any_diff() is True


def test_any_diff_false_when_identical(tmp_path):
    f1 = tmp_path / "f1.env"
    f2 = tmp_path / "f2.env"
    f1.write_text("A=1\n")
    f2.write_text("A=1\n")
    result = diff_many(str(f1), [str(f2)])
    assert result.any_diff() is False


def test_total_missing_b(env_files):
    base, a, b = env_files
    result = diff_many(base, [b])
    assert result.total_missing_b() == 1


def test_total_mismatches(env_files):
    base, a, b = env_files
    result = diff_many(base, [a])
    assert result.total_mismatches() == 1


def test_summary_contains_labels(env_files):
    base, a, b = env_files
    result = diff_many(base, [a, b])
    summary = result.summary()
    assert "DIFF" in summary


def test_total_missing_a(tmp_path):
    base = tmp_path / "base.env"
    other = tmp_path / "other.env"
    base.write_text("A=1\n")
    other.write_text("A=1\nB=2\n")
    result = diff_many(str(base), [str(other)])
    assert result.total_missing_a() == 1
