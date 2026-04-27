"""Tests for envdiff.comparator_stats_formatter."""
from __future__ import annotations

import json

import pytest

from envdiff.comparator_stats import ComparatorStats
from envdiff.comparator_stats_formatter import format_text, format_json


@pytest.fixture
def clean_stats():
    return ComparatorStats(
        total_pairs=2,
        clean_pairs=2,
        dirty_pairs=0,
        total_missing_a=0,
        total_missing_b=0,
        total_mismatches=0,
        labels=["a:b", "c:d"],
    )


@pytest.fixture
def dirty_stats():
    return ComparatorStats(
        total_pairs=3,
        clean_pairs=1,
        dirty_pairs=2,
        total_missing_a=1,
        total_missing_b=2,
        total_mismatches=3,
        labels=[],
    )


def test_format_text_no_diff(clean_stats):
    out = format_text(clean_stats, color=False)
    assert "Clean pairs     : 2" in out
    assert "Dirty pairs     : 0" in out


def test_format_text_shows_dirty(dirty_stats):
    out = format_text(dirty_stats, color=False)
    assert "Dirty pairs     : 2" in out
    assert "Mismatches      : 3" in out


def test_format_text_diff_rate(dirty_stats):
    out = format_text(dirty_stats, color=False)
    assert "67%" in out


def test_format_text_labels_shown(clean_stats):
    out = format_text(clean_stats, color=False)
    assert "a:b" in out
    assert "c:d" in out


def test_format_text_no_labels_section_when_empty(dirty_stats):
    out = format_text(dirty_stats, color=False)
    assert "Pairs:" not in out


def test_format_json_valid(dirty_stats):
    raw = format_json(dirty_stats)
    data = json.loads(raw)
    assert data["total_pairs"] == 3
    assert data["dirty_pairs"] == 2
    assert "diff_rate" in data


def test_format_json_diff_rate_rounded(dirty_stats):
    raw = format_json(dirty_stats)
    data = json.loads(raw)
    assert data["diff_rate"] == pytest.approx(0.6667, abs=1e-3)


def test_format_json_labels_field(clean_stats):
    raw = format_json(clean_stats)
    data = json.loads(raw)
    assert data["labels"] == ["a:b", "c:d"]
