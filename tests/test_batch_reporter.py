"""Tests for envdiff.batch_reporter."""
import json
import pytest
from envdiff.differ_plus import diff_many
from envdiff.batch_reporter import render_text, render_json, exit_code


@pytest.fixture
def clean_multi(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("Xb.write_text("X=1\n")
    return diff_many(str(a), [str(b)])


@pytest.fixture
def dirty_multi(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("X=1\nY=2\n")
    b.write_text("X=changed\n")
    return diff_many(str(a), [str(b)])


def test_render_text_no_diff(clean_multi):
    out = render_text(clean_multi)
    assert "No differences" in out


def test_render_text_mismatch(dirty_multi):
    out = render_text(dirty_multi)
    assert "mismatch" in out


def test_render_text_missing_b(dirty_multi):
    out = render_text(dirty_multi)
    assert "+B missing" in out


def test_render_json_valid(dirty_multi):
    out = render_json(dirty_multi)
    parsed = json.loads(out)
    assert isinstance(parsed, dict)
    assert len(parsed) == 1


def test_render_json_has_mismatches(dirty_multi):
    parsed = json.loads(render_json(dirty_multi))
    values = list(parsed.values())[0]
    assert "mismatches" in values


def test_exit_code_clean(clean_multi):
    assert exit_code(clean_multi) == 0


def test_exit_code_dirty(dirty_multi):
    assert exit_code(dirty_multi) == 1
