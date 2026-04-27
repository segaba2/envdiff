"""Tests for envdiff.comparator_stats."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.comparator_stats import ComparatorStats, compute_comparator_stats


def _make(missing_a=(), missing_b=(), mismatches=(), common=()):
    return DiffResult(
        missing_in_a=list(missing_a),
        missing_in_b=list(missing_b),
        mismatches=dict(mismatches),
        common=dict(common),
    )


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def clean_pair():
    return _make(common=[("KEY", "val")])


@pytest.fixture
def dirty_pair():
    return _make(
        missing_a=["ONLY_B"],
        missing_b=["ONLY_A"],
        mismatches=[("SHARED", ("x", "y"))],
    )


# ── tests ─────────────────────────────────────────────────────────────────────

def test_empty_list_returns_zero_stats():
    stats = compute_comparator_stats([])
    assert stats.total_pairs == 0
    assert stats.diff_rate == 0.0


def test_clean_pair_counted(clean_pair):
    stats = compute_comparator_stats([clean_pair])
    assert stats.total_pairs == 1
    assert stats.clean_pairs == 1
    assert stats.dirty_pairs == 0


def test_dirty_pair_counted(dirty_pair):
    stats = compute_comparator_stats([dirty_pair])
    assert stats.dirty_pairs == 1
    assert stats.clean_pairs == 0


def test_missing_counts_accumulated(dirty_pair):
    stats = compute_comparator_stats([dirty_pair, dirty_pair])
    assert stats.total_missing_a == 2
    assert stats.total_missing_b == 2
    assert stats.total_mismatches == 2


def test_diff_rate_calculation(clean_pair, dirty_pair):
    stats = compute_comparator_stats([clean_pair, dirty_pair])
    assert stats.diff_rate == pytest.approx(0.5)


def test_labels_stored():
    stats = compute_comparator_stats([], labels=["a:b", "c:d"])
    assert stats.labels == ["a:b", "c:d"]


def test_summary_string_contains_key_fields(dirty_pair):
    stats = compute_comparator_stats([dirty_pair])
    s = stats.summary()
    assert "pairs=1" in s
    assert "dirty=1" in s
    assert "diff_rate=" in s


def test_total_keys_compared(clean_pair, dirty_pair):
    stats = compute_comparator_stats([clean_pair, dirty_pair])
    # clean has 1 common key; dirty has 3 distinct keys
    assert stats.total_keys_compared == 4
