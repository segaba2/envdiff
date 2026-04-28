"""Tests for envdiff.sanitizer."""
from __future__ import annotations

import pytest

from envdiff.sanitizer import sanitize, SanitizeResult


@pytest.fixture()
def sample_env() -> dict:
    return {
        "CLEAN_KEY": "hello_world",
        "SHELL_INJECT": "value;rm -rf /",
        "BACKTICK": "val`cmd`",
        "PIPE_KEY": "foo|bar",
        "NEWLINE_KEY": "line1\nline2",
        "CONTROL_CHAR": "val\x01ue",
    }


def test_returns_sanitize_result(sample_env):
    result = sanitize(sample_env)
    assert isinstance(result, SanitizeResult)


def test_clean_key_unchanged(sample_env):
    result = sanitize(sample_env)
    assert result.sanitized["CLEAN_KEY"] == "hello_world"


def test_semicolon_removed(sample_env):
    result = sanitize(sample_env)
    assert ";" not in result.sanitized["SHELL_INJECT"]


def test_backtick_removed(sample_env):
    result = sanitize(sample_env)
    assert "`" not in result.sanitized["BACKTICK"]


def test_pipe_removed(sample_env):
    result = sanitize(sample_env)
    assert "|" not in result.sanitized["PIPE_KEY"]


def test_newline_replaced_with_space(sample_env):
    result = sanitize(sample_env)
    assert "\n" not in result.sanitized["NEWLINE_KEY"]
    assert " " in result.sanitized["NEWLINE_KEY"]


def test_newline_kept_when_strip_disabled(sample_env):
    result = sanitize(sample_env, strip_newlines=False)
    assert "\n" in result.sanitized["NEWLINE_KEY"]


def test_control_char_removed(sample_env):
    result = sanitize(sample_env)
    assert "\x01" not in result.sanitized["CONTROL_CHAR"]


def test_changed_keys_lists_dirty_keys(sample_env):
    result = sanitize(sample_env)
    assert "CLEAN_KEY" not in result.changed_keys
    for key in ("SHELL_INJECT", "BACKTICK", "PIPE_KEY", "NEWLINE_KEY", "CONTROL_CHAR"):
        assert key in result.changed_keys


def test_has_changes_true_when_dirty(sample_env):
    result = sanitize(sample_env)
    assert result.has_changes() is True


def test_has_changes_false_when_clean():
    result = sanitize({"A": "clean", "B": "also_clean"})
    assert result.has_changes() is False


def test_summary_clean():
    result = sanitize({"X": "fine"})
    assert "no sanitization" in result.summary()


def test_summary_dirty(sample_env):
    result = sanitize(sample_env)
    assert "sanitized" in result.summary()


def test_replacement_string_used():
    result = sanitize({"K": "a;b"}, replacement="_")
    assert result.sanitized["K"] == "a_b"


def test_only_keys_restricts_sanitization(sample_env):
    result = sanitize(sample_env, only_keys=["CLEAN_KEY"])
    # SHELL_INJECT should be untouched because it's not in only_keys
    assert result.sanitized["SHELL_INJECT"] == sample_env["SHELL_INJECT"]
    assert "SHELL_INJECT" not in result.changed_keys


def test_original_preserved(sample_env):
    result = sanitize(sample_env)
    assert result.original == sample_env
    # Ensure original is a copy, not the same object
    result.sanitized["CLEAN_KEY"] = "mutated"
    assert result.original["CLEAN_KEY"] == "hello_world"
