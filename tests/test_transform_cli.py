"""Tests for envdiff.transform_cli."""
import json
from pathlib import Path

import pytest

from envdiff.transform_cli import run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "db_host=localhost\n"
        "api_key=  secret  \n"
        "DEBUG=true\n"
    )
    return f


def _run(args):
    """Helper that captures SystemExit and returns exit code."""
    try:
        return run(args)
    except SystemExit as exc:
        return int(exc.code)


def test_exit_zero_on_valid_file(env_file):
    assert _run([str(env_file)]) == 0


def test_exit_one_on_missing_file(tmp_path):
    assert _run([str(tmp_path / "missing.env")]) == 1


def test_upper_keys_in_text_output(env_file, capsys):
    _run([str(env_file), "--upper-keys"])
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "API_KEY" in out


def test_strip_values_in_text_output(env_file, capsys):
    _run([str(env_file), "--strip-values"])
    out = capsys.readouterr().out
    # value should be stripped
    assert "secret" in out
    # no leading/trailing spaces around 'secret'
    assert "  secret  " not in out


def test_json_output_structure(env_file, capsys):
    _run([str(env_file), "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "transformed" in data
    assert "applied" in data


def test_rename_via_cli(env_file, capsys):
    _run([str(env_file), "--rename", "DEBUG=DEBUG_MODE"])
    out = capsys.readouterr().out
    assert "DEBUG_MODE" in out
    assert "DEBUG=" not in out


def test_invalid_rename_exits_one(env_file):
    assert _run([str(env_file), "--rename", "NODIVIDER"]) == 1


def test_applied_marker_present_in_text(env_file, capsys):
    _run([str(env_file), "--upper-keys"])
    out = capsys.readouterr().out
    # transformed keys are marked with '*'
    assert "[*]" in out
