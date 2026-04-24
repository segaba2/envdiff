"""Tests for envdiff.smart_diff_formatter."""
import json
import pytest
from envdiff.comparator_plus import smart_compare
from envdiff.smart_diff_formatter import format_text, format_json


@pytest.fixture
def clean_result():
    return smart_compare({"A": "1", "B": "2"}, {"A": "1", "B": "2"})


@pytest.fixture
def dirty_result():
    return smart_compare(
        {"A": "hello", "B": "1", "C": "gone"},
        {"A": "HELLO", "B": "true", "D": "new"},
    )


# ---------------------------------------------------------------------------
# format_text — clean
# ---------------------------------------------------------------------------

def test_format_text_no_diff(clean_result):
    out = format_text(clean_result)
    assert "No differences" in out

def test_format_text_no_diff_no_color(clean_result):
    out = format_text(clean_result, use_color=False)
    assert "\033[" not in out


# ---------------------------------------------------------------------------
# format_text — diff content
# ---------------------------------------------------------------------------

def test_format_text_shows_mismatch(dirty_result):
    out = format_text(dirty_result)
    assert "mismatch" in out

def test_format_text_case_only_label(dirty_result):
    out = format_text(dirty_result)
    assert "case-only" in out

def test_format_text_type_mismatch_label(dirty_result):
    out = format_text(dirty_result)
    assert "type-mismatch" in out

def test_format_text_missing_in_a(dirty_result):
    out = format_text(dirty_result)
    assert "missing in A" in out

def test_format_text_missing_in_b(dirty_result):
    out = format_text(dirty_result)
    assert "missing in B" in out

def test_format_text_includes_summary(dirty_result):
    out = format_text(dirty_result)
    assert "mismatches=" in out


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

def test_format_json_valid(dirty_result):
    raw = format_json(dirty_result)
    data = json.loads(raw)
    assert "has_diff" in data
    assert "entries" in data
    assert isinstance(data["entries"], list)

def test_format_json_clean_has_diff_false(clean_result):
    data = json.loads(format_json(clean_result))
    assert data["has_diff"] is False

def test_format_json_dirty_has_diff_true(dirty_result):
    data = json.loads(format_json(dirty_result))
    assert data["has_diff"] is True

def test_format_json_entry_fields(dirty_result):
    data = json.loads(format_json(dirty_result))
    entry = data["entries"][0]
    for field in ("key", "value_a", "value_b", "status", "case_only", "type_mismatch"):
        assert field in entry
