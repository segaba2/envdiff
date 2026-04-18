"""Tests for envdiff.formatter module."""

import json
import pytest
from envdiff.comparator import DiffResult
from envdiff.formatter import format_text, format_json


@pytest.fixture
def clean_result():
    return DiffResult(missing_in_a=set(), missing_in_b=set(), mismatched={})


@pytest.fixture
def diff_result():
    return DiffResult(
        missing_in_a={"ONLY_IN_B"},
        missing_in_b={"ONLY_IN_A"},
        mismatched={"SHARED": ("val1", "val2")},
    )


def test_format_text_no_diff(clean_result):
    output = format_text(clean_result, "dev", "prod", use_color=False)
    assert "No differences found" in output
    assert "dev vs prod" in output


def test_format_text_missing_in_a(diff_result):
    output = format_text(diff_result, "dev", "prod", use_color=False)
    assert "ONLY_IN_B" in output
    assert "missing in dev" in output


def test_format_text_missing_in_b(diff_result):
    output = format_text(diff_result, "dev", "prod", use_color=False)
    assert "ONLY_IN_A" in output
    assert "missing in prod" in output


def test_format_text_mismatch(diff_result):
    output = format_text(diff_result, "dev", "prod", use_color=False)
    assert "SHARED" in output
    assert "val1" in output
    assert "val2" in output


def test_format_text_summary_included(diff_result):
    output = format_text(diff_result, "dev", "prod", use_color=False)
    assert "missing" in output.lower() or "mismatch" in output.lower()


def test_format_json_no_diff(clean_result):
    raw = format_json(clean_result, "dev", "prod")
    data = json.loads(raw)
    assert data["has_diff"] is False
    assert data["missing_in_a"] == []
    assert data["missing_in_b"] == []
    assert data["mismatched"] == {}


def test_format_json_with_diff(diff_result):
    raw = format_json(diff_result, "dev", "prod")
    data = json.loads(raw)
    assert data["has_diff"] is True
    assert "ONLY_IN_B" in data["missing_in_a"]
    assert "ONLY_IN_A" in data["missing_in_b"]
    assert "SHARED" in data["mismatched"]
    assert data["mismatched"]["SHARED"]["dev"] == "val1"
    assert data["mismatched"]["SHARED"]["prod"] == "val2"


def test_format_text_color_codes_absent_when_disabled(diff_result):
    output = format_text(diff_result, "dev", "prod", use_color=False)
    assert "\033[" not in output


def test_format_text_color_codes_present_when_enabled(diff_result):
    output = format_text(diff_result, "dev", "prod", use_color=True)
    assert "\033[" in output
