"""Tests for envdiff.drift_cli — CLI wrapper around drifter."""
import json
import os
import pytest
from pathlib import Path
from click.testing import CliRunner
from envdiff.drift_cli import main
from envdiff.snapshotter import Snapshot


@pytest.fixture
def env_dir(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return tmp_path, env_file


def _save_snapshot(path: Path, data: dict) -> Path:
    snap = Snapshot(env_file=str(path), keys=data)
    snap_path = path.parent / "snap.json"
    snap.save(str(snap_path))
    return snap_path


def _run(args):
    runner = CliRunner()
    return runner.invoke(main, args, catch_exceptions=False)


def test_exit_zero_on_no_drift(env_dir):
    _, env_file = env_dir
    snap_path = _save_snapshot(
        env_file,
        {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"},
    )
    result = _run([str(env_file), str(snap_path)])
    assert result.exit_code == 0


def test_exit_nonzero_on_drift(env_dir):
    _, env_file = env_dir
    snap_path = _save_snapshot(
        env_file,
        {"DB_HOST": "localhost", "DB_PORT": "5432"},  # missing SECRET_KEY
    )
    result = _run([str(env_file), str(snap_path)])
    assert result.exit_code != 0


def test_text_output_shows_added_key(env_dir):
    _, env_file = env_dir
    snap_path = _save_snapshot(
        env_file,
        {"DB_HOST": "localhost", "DB_PORT": "5432"},
    )
    result = _run([str(env_file), str(snap_path), "--format", "text"])
    assert "SECRET_KEY" in result.output


def test_json_output_is_valid(env_dir):
    _, env_file = env_dir
    snap_path = _save_snapshot(
        env_file,
        {"DB_HOST": "localhost", "DB_PORT": "5432"},
    )
    result = _run([str(env_file), str(snap_path), "--format", "json"])
    parsed = json.loads(result.output)
    assert "added" in parsed or "removed" in parsed or "changed" in parsed


def test_removed_key_detected(env_dir):
    _, env_file = env_dir
    snap_path = _save_snapshot(
        env_file,
        {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "SECRET_KEY": "abc123",
            "OLD_KEY": "old_value",
        },
    )
    result = _run([str(env_file), str(snap_path), "--format", "text"])
    assert "OLD_KEY" in result.output
    assert result.exit_code != 0


def test_changed_value_detected(env_dir):
    _, env_file = env_dir
    snap_path = _save_snapshot(
        env_file,
        {"DB_HOST": "remotehost", "DB_PORT": "5432", "SECRET_KEY": "abc123"},
    )
    result = _run([str(env_file), str(snap_path), "--format", "text"])
    assert "DB_HOST" in result.output
    assert result.exit_code != 0
