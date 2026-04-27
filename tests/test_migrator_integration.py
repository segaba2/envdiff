"""Integration tests: parse .env then migrate."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.migrator import migrate
from envdiff.parser import parse_env_file


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "# comment\n"
        "SECRET_KEY=supersecret\n"
        "LEGACY_TOKEN=oldtoken\n"
    )
    return p


def test_parse_then_migrate_rename(env_file):
    env = parse_env_file(env_file)
    result = migrate(env, rename_map={"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.migrated
    assert result.migrated["DATABASE_HOST"] == "localhost"


def test_parse_then_migrate_drop(env_file):
    env = parse_env_file(env_file)
    result = migrate(env, drop_keys=["LEGACY_TOKEN"])
    assert "LEGACY_TOKEN" not in result.migrated
    assert "LEGACY_TOKEN" in result.dropped


def test_parse_then_migrate_transform(env_file):
    env = parse_env_file(env_file)
    result = migrate(env, transforms={"DB_PORT": lambda v: str(int(v) + 1)})
    assert result.migrated["DB_PORT"] == "5433"


def test_parse_comments_not_in_migrated(env_file):
    env = parse_env_file(env_file)
    result = migrate(env)
    assert all(not k.startswith("#") for k in result.migrated)


def test_full_pipeline_rename_drop_transform(env_file):
    env = parse_env_file(env_file)
    result = migrate(
        env,
        rename_map={"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"},
        drop_keys=["LEGACY_TOKEN"],
        transforms={"DATABASE_PORT": lambda v: str(int(v) * 2)},
    )
    assert result.migrated["DATABASE_HOST"] == "localhost"
    assert result.migrated["DATABASE_PORT"] == "10864"
    assert "LEGACY_TOKEN" not in result.migrated
    assert not result.has_errors()
