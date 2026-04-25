"""Tests for envdiff.scope_cli."""
import json
from pathlib import Path
import pytest
from envdiff.scope_cli import run


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_HOST=localhost\n"
        "APP_PORT=8080\n"
        "DB_HOST=db.local\n"
        "SECRET_KEY=s3cr3t\n"
    )
    return p


def _run(args):
    return run(args)


def test_exit_zero_on_valid_file(env_file):
    assert _run([str(env_file), "app"]) == 0


def test_exit_one_on_missing_file(tmp_path):
    assert _run([str(tmp_path / "missing.env"), "app"]) == 1


def test_text_output_shows_matched_keys(env_file, capsys):
    _run([str(env_file), "app"])
    out = capsys.readouterr().out
    assert "APP_HOST" in out
    assert "APP_PORT" in out


def test_text_output_hides_excluded_by_default(env_file, capsys):
    _run([str(env_file), "app"])
    out = capsys.readouterr().out
    assert "DB_HOST" not in out


def test_show_excluded_flag(env_file, capsys):
    _run([str(env_file), "app", "--show-excluded"])
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "SECRET_KEY" in out


def test_json_output_is_valid(env_file, capsys):
    _run([str(env_file), "app", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["scope"] == "app"
    assert "APP_HOST" in data["matched"]


def test_strip_prefix_in_json(env_file, capsys):
    _run([str(env_file), "app", "--format", "json", "--strip-prefix"])
    data = json.loads(capsys.readouterr().out)
    assert "HOST" in data["matched"]
    assert data["strip_prefix"] is True


def test_explicit_prefix_override(env_file, capsys):
    _run([str(env_file), "database", "--prefix", "DB_", "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert "DB_HOST" in data["matched"]
    assert "APP_HOST" not in data["matched"]
