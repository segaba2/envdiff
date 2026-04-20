"""Tests for envdiff.trimmer and envdiff.trim_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.trimmer import trim, trim_to_template, TrimResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def full_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
        "LEGACY_FLAG": "true",
        "OLD_API_URL": "http://old.example.com",
    }


@pytest.fixture
def template() -> dict:
    return {
        "DB_HOST": "",
        "DB_PORT": "",
        "SECRET_KEY": "",
    }


# ---------------------------------------------------------------------------
# trim()
# ---------------------------------------------------------------------------

def test_trim_keeps_reference_keys(full_env, template):
    result = trim(full_env, set(template.keys()))
    assert set(result.kept.keys()) == {"DB_HOST", "DB_PORT", "SECRET_KEY"}


def test_trim_removes_stale_keys(full_env, template):
    result = trim(full_env, set(template.keys()))
    assert "LEGACY_FLAG" in result.removed
    assert "OLD_API_URL" in result.removed


def test_trim_removed_is_sorted(full_env, template):
    result = trim(full_env, set(template.keys()))
    assert result.removed == sorted(result.removed)


def test_trim_values_preserved(full_env, template):
    result = trim(full_env, set(template.keys()))
    assert result.kept["DB_HOST"] == "localhost"
    assert result.kept["SECRET_KEY"] == "abc123"


def test_trim_no_removals_when_all_in_reference(full_env):
    result = trim(full_env, set(full_env.keys()))
    assert not result.has_removals()
    assert result.removed == []


def test_trim_ignore_case():
    env = {"db_host": "localhost", "STALE": "old"}
    ref = {"DB_HOST"}  # upper-case reference
    result = trim(env, ref, ignore_case=True)
    assert "db_host" in result.kept
    assert "STALE" in result.removed


# ---------------------------------------------------------------------------
# trim_to_template()
# ---------------------------------------------------------------------------

def test_trim_to_template_convenience(full_env, template):
    result = trim_to_template(full_env, template)
    assert isinstance(result, TrimResult)
    assert len(result.kept) == 3


# ---------------------------------------------------------------------------
# TrimResult helpers
# ---------------------------------------------------------------------------

def test_has_removals_true(full_env, template):
    result = trim_to_template(full_env, template)
    assert result.has_removals() is True


def test_has_removals_false():
    env = {"A": "1"}
    result = trim(env, {"A"})
    assert result.has_removals() is False


def test_summary_no_removals():
    env = {"A": "1"}
    result = trim(env, {"A"})
    assert "nothing to trim" in result.summary().lower()


def test_summary_with_removals(full_env, template):
    result = trim_to_template(full_env, template)
    s = result.summary()
    assert "stale" in s.lower()
    assert "2" in s  # two stale keys


# ---------------------------------------------------------------------------
# trim_cli via subprocess-style invocation
# ---------------------------------------------------------------------------

def test_cli_exit_zero_no_removals(tmp_path):
    from envdiff.trim_cli import run

    env_file = tmp_path / ".env"
    ref_file = tmp_path / ".env.template"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    ref_file.write_text("DB_HOST=\nDB_PORT=\n")

    code = run([str(env_file), "--reference", str(ref_file)])
    assert code == 0


def test_cli_exit_one_on_removals(tmp_path):
    from envdiff.trim_cli import run

    env_file = tmp_path / ".env"
    ref_file = tmp_path / ".env.template"
    env_file.write_text("DB_HOST=localhost\nSTALE=old\n")
    ref_file.write_text("DB_HOST=\n")

    code = run([str(env_file), "--reference", str(ref_file)])
    assert code == 1


def test_cli_json_output(tmp_path, capsys):
    from envdiff.trim_cli import run

    env_file = tmp_path / ".env"
    ref_file = tmp_path / ".env.template"
    env_file.write_text("A=1\nB=2\n")
    ref_file.write_text("A=\n")

    run([str(env_file), "--reference", str(ref_file), "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "kept" in data
    assert "removed" in data
    assert "B" in data["removed"]


def test_cli_in_place_writes_file(tmp_path):
    from envdiff.trim_cli import run

    env_file = tmp_path / ".env"
    ref_file = tmp_path / ".env.template"
    env_file.write_text("KEEP=yes\nSTALE=no\n")
    ref_file.write_text("KEEP=\n")

    run([str(env_file), "--reference", str(ref_file), "--in-place"])
    content = env_file.read_text()
    assert "KEEP" in content
    assert "STALE" not in content


def test_cli_missing_env_file_returns_2(tmp_path):
    from envdiff.trim_cli import run

    ref_file = tmp_path / ".env.template"
    ref_file.write_text("A=\n")
    code = run([str(tmp_path / "ghost.env"), "--reference", str(ref_file)])
    assert code == 2
