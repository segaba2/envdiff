"""Unit tests for envdiff.migrator."""
from __future__ import annotations

import pytest

from envdiff.migrator import MigrateResult, migrate


@pytest.fixture()
def base_env() -> dict[str, str]:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
        "OLD_NAME": "value",
        "LEGACY": "drop_me",
    }


def test_returns_migrate_result(base_env):
    result = migrate(base_env)
    assert isinstance(result, MigrateResult)


def test_no_map_keeps_all_keys(base_env):
    result = migrate(base_env)
    assert set(result.migrated.keys()) == set(base_env.keys())


def test_rename_applied(base_env):
    result = migrate(base_env, rename_map={"OLD_NAME": "NEW_NAME"})
    assert "NEW_NAME" in result.migrated
    assert "OLD_NAME" not in result.migrated
    assert result.migrated["NEW_NAME"] == "value"


def test_drop_removes_key(base_env):
    result = migrate(base_env, drop_keys=["LEGACY"])
    assert "LEGACY" not in result.migrated
    assert "LEGACY" in result.dropped


def test_drop_does_not_affect_other_keys(base_env):
    result = migrate(base_env, drop_keys=["LEGACY"])
    assert "DB_HOST" in result.migrated


def test_keep_unmapped_false_omits_unmapped(base_env):
    result = migrate(base_env, rename_map={"DB_HOST": "DATABASE_HOST"}, keep_unmapped=False)
    assert set(result.migrated.keys()) == {"DATABASE_HOST"}
    assert len(result.skipped) == len(base_env) - 1


def test_transform_applied(base_env):
    result = migrate(base_env, transforms={"DB_PORT": int})
    # value is stored as result of transform; coerce back for assertion
    assert result.migrated["DB_PORT"] == 5432  # type: ignore[comparison-overlap]


def test_transform_error_recorded(base_env):
    def boom(v: str) -> str:
        raise ValueError("bad value")

    result = migrate({"X": "y"}, transforms={"X": boom})
    assert result.has_errors()
    assert any("X" in e for e in result.errors)
    assert "X" not in result.migrated


def test_summary_string(base_env):
    result = migrate(base_env, drop_keys=["LEGACY"])
    s = result.summary()
    assert "migrated=" in s
    assert "dropped=" in s


def test_no_errors_on_clean_migration(base_env):
    result = migrate(base_env)
    assert not result.has_errors()


def test_rename_and_drop_combined(base_env):
    result = migrate(base_env, rename_map={"OLD_NAME": "NEW_NAME"}, drop_keys=["LEGACY"])
    assert "NEW_NAME" in result.migrated
    assert "LEGACY" not in result.migrated
    assert "LEGACY" in result.dropped
