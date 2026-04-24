"""Tests for envdiff.aliaser."""
import pytest
from envdiff.aliaser import alias, AliasResult


@pytest.fixture()
def base_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "hunter2",
        "OLD_API_KEY": "abc123",
    }


def test_returns_alias_result(base_env):
    result = alias(base_env, {})
    assert isinstance(result, AliasResult)


def test_no_aliases_returns_copy(base_env):
    result = alias(base_env, {})
    assert result.env == base_env
    assert result.applied == {}
    assert result.missing == []
    assert result.conflicts == {}


def test_alias_promoted_when_canonical_absent(base_env):
    result = alias(base_env, {"OLD_API_KEY": "API_KEY"})
    assert "API_KEY" in result.env
    assert result.env["API_KEY"] == "abc123"
    assert "OLD_API_KEY" not in result.env
    assert result.applied == {"OLD_API_KEY": "API_KEY"}


def test_alias_not_promoted_when_canonical_present():
    env = {"API_KEY": "newvalue", "OLD_API_KEY": "oldvalue"}
    result = alias(env, {"OLD_API_KEY": "API_KEY"})
    # canonical already present and values differ -> conflict
    assert result.env["API_KEY"] == "newvalue"
    assert "OLD_API_KEY" not in result.env
    assert "API_KEY" in result.conflicts
    assert "OLD_API_KEY" in result.conflicts["API_KEY"]


def test_no_conflict_when_values_identical():
    env = {"API_KEY": "same", "OLD_API_KEY": "same"}
    result = alias(env, {"OLD_API_KEY": "API_KEY"})
    assert result.conflicts == {}
    assert "OLD_API_KEY" not in result.env


def test_missing_when_neither_present():
    result = alias({"OTHER": "val"}, {"OLD_TOKEN": "TOKEN"})
    assert "TOKEN" in result.missing
    assert result.applied == {}


def test_multiple_aliases_applied():
    env = {"OLD_HOST": "localhost", "OLD_PORT": "5432"}
    result = alias(env, {"OLD_HOST": "DB_HOST", "OLD_PORT": "DB_PORT"})
    assert result.env["DB_HOST"] == "localhost"
    assert result.env["DB_PORT"] == "5432"
    assert len(result.applied) == 2


def test_summary_no_changes(base_env):
    result = alias(base_env, {})
    assert result.summary() == "no changes"


def test_summary_with_applied(base_env):
    result = alias(base_env, {"OLD_API_KEY": "API_KEY"})
    assert "applied" in result.summary()


def test_summary_with_missing():
    result = alias({}, {"OLD_FOO": "FOO"})
    assert "missing" in result.summary()


def test_has_conflicts_false_when_clean(base_env):
    result = alias(base_env, {"OLD_API_KEY": "API_KEY"})
    assert not result.has_conflicts()


def test_has_conflicts_true_on_conflict():
    env = {"KEY": "a", "OLD_KEY": "b"}
    result = alias(env, {"OLD_KEY": "KEY"})
    assert result.has_conflicts()
