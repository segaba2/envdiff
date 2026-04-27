"""CLI tests for envdiff.migrate_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.migrate_cli import run


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _run(*args: str) -> int:
    return run(list(args))


def test_exit_zero_on_valid_file(env_dir):
    src = _write(env_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    assert _run(str(src)) == 0


def test_exit_one_on_missing_file(env_dir):
    assert _run(str(env_dir / "missing.env")) == 1


def test_rename_via_map_file(env_dir):
    src = _write(env_dir / ".env", "OLD_KEY=hello\n")
    map_file = env_dir / "map.json"
    map_file.write_text(json.dumps({"OLD_KEY": "NEW_KEY"}))
    out = env_dir / "out.env"
    assert _run(str(src), "--map", str(map_file), "--out", str(out)) == 0
    content = out.read_text()
    assert "NEW_KEY=hello" in content
    assert "OLD_KEY" not in content


def test_drop_key_via_cli(env_dir):
    src = _write(env_dir / ".env", "KEEP=yes\nDROP=no\n")
    out = env_dir / "out.env"
    assert _run(str(src), "--drop", "DROP", "--out", str(out)) == 0
    content = out.read_text()
    assert "KEEP=yes" in content
    assert "DROP" not in content


def test_json_output_is_valid(env_dir, capsys):
    src = _write(env_dir / ".env", "FOO=bar\n")
    assert _run(str(src), "--format", "json") == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "migrated" in data
    assert data["migrated"]["FOO"] == "bar"


def test_missing_map_file_exits_one(env_dir):
    src = _write(env_dir / ".env", "FOO=bar\n")
    assert _run(str(src), "--map", str(env_dir / "no_map.json")) == 1
