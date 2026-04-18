import pytest
from envdiff.renamer import rename, suggest_renames, RenameResult


@pytest.fixture
def env():
    return {"OLD_HOST": "localhost", "PORT": "8080", "DEBUG": "true"}


def test_rename_applies_mapping(env):
    result = rename(env, {"OLD_HOST": "HOST"})
    assert "HOST" in result.env
    assert "OLD_HOST" not in result.env
    assert result.env["HOST"] == "localhost"


def test_rename_preserves_other_keys(env):
    result = rename(env, {"OLD_HOST": "HOST"})
    assert result.env["PORT"] == "8080"
    assert result.env["DEBUG"] == "true"


def test_rename_records_applied(env):
    result = rename(env, {"OLD_HOST": "HOST", "PORT": "APP_PORT"})
    assert result.applied == {"OLD_HOST": "HOST", "PORT": "APP_PORT"}


def test_rename_records_skipped_when_key_missing(env):
    result = rename(env, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert result.applied == {}


def test_rename_summary_applied(env):
    result = rename(env, {"OLD_HOST": "HOST"})
    assert "1 renamed" in result.summary()


def test_rename_summary_skipped(env):
    result = rename(env, {"GHOST": "SPIRIT"})
    assert "1 not found" in result.summary()


def test_rename_summary_nothing():
    result = rename({}, {})
    assert result.summary() == "nothing to rename"


def test_suggest_renames_finds_same_value():
    a = {"DB_PASS": "secret123", "HOST": "localhost"}
    b = {"DATABASE_PASSWORD": "secret123", "HOST": "localhost"}
    suggestions = suggest_renames(a, b)
    assert ("DB_PASS", "DATABASE_PASSWORD") in suggestions


def test_suggest_renames_ignores_blank_values():
    a = {"EMPTY": ""}
    b = {"ALSO_EMPTY": ""}
    suggestions = suggest_renames(a, b)
    assert suggestions == []


def test_suggest_renames_no_suggestions_when_keys_match():
    env = {"HOST": "localhost"}
    suggestions = suggest_renames(env, env)
    assert suggestions == []
