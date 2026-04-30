"""Tests for envdiff.stack_formatter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.stacker import stack
from envdiff.stack_formatter import format_json, format_text


@pytest.fixture()
def env_dir(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


@pytest.fixture()
def clean_result(env_dir):
    f = env_dir("base.env", "FOO=bar\nBAZ=qux\n")
    return stack([f])


@pytest.fixture()
def override_result(env_dir):
    base = env_dir("base.env", "KEY=original\nOTHER=x\n")
    over = env_dir("over.env", "KEY=new\n")
    return stack([base, over])


def test_format_text_no_override(clean_result):
    out = format_text(clean_result, use_color=False)
    assert "FOO=bar" in out
    assert "BAZ=qux" in out
    assert "[overridden]" not in out


def test_format_text_shows_overridden(override_result):
    out = format_text(override_result, use_color=False)
    assert "[overridden]" in out


def test_format_text_shows_summary(clean_result):
    out = format_text(clean_result, use_color=False)
    assert "key(s) resolved" in out


def test_format_text_empty_result(env_dir):
    f = env_dir("empty.env", "# comment\n")
    result = stack([f])
    out = format_text(result, use_color=False)
    assert "No keys" in out


def test_format_json_valid(clean_result):
    raw = format_json(clean_result)
    data = json.loads(raw)
    assert "entries" in data
    assert "summary" in data
    assert "files" in data


def test_format_json_entries_have_required_fields(override_result):
    data = json.loads(format_json(override_result))
    for entry in data["entries"]:
        assert "key" in entry
        assert "value" in entry
        assert "source" in entry
        assert "overridden_by" in entry


def test_format_json_overridden_key_marked(override_result):
    data = json.loads(format_json(override_result))
    key_entry = next(e for e in data["entries"] if e["key"] == "KEY")
    assert key_entry["overridden_by"] is not None
