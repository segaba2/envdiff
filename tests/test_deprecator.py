"""Tests for envdiff.deprecator."""
import pytest
from envdiff.deprecator import deprecate, DeprecateResult, DeprecationEntry


DEP_MAP = {
    "OLD_API_KEY": {"reason": "Renamed", "replacement": "API_KEY"},
    "LEGACY_HOST": {"reason": "No longer supported"},
}


@pytest.fixture()
def mixed_env():
    return {
        "OLD_API_KEY": "abc123",
        "LEGACY_HOST": "localhost",
        "DATABASE_URL": "postgres://localhost/db",
        "APP_PORT": "8080",
    }


def test_returns_deprecate_result(mixed_env):
    result = deprecate(mixed_env, DEP_MAP)
    assert isinstance(result, DeprecateResult)


def test_deprecated_keys_detected(mixed_env):
    result = deprecate(mixed_env, DEP_MAP)
    keys = [e.key for e in result.deprecated]
    assert "OLD_API_KEY" in keys
    assert "LEGACY_HOST" in keys


def test_clean_keys_not_in_deprecated(mixed_env):
    result = deprecate(mixed_env, DEP_MAP)
    dep_keys = {e.key for e in result.deprecated}
    assert "DATABASE_URL" not in dep_keys
    assert "APP_PORT" not in dep_keys


def test_clean_list_contains_non_deprecated(mixed_env):
    result = deprecate(mixed_env, DEP_MAP)
    assert "DATABASE_URL" in result.clean
    assert "APP_PORT" in result.clean


def test_replacement_captured():
    env = {"OLD_API_KEY": "val"}
    result = deprecate(env, DEP_MAP)
    entry = result.deprecated[0]
    assert entry.replacement == "API_KEY"


def test_no_replacement_when_absent():
    env = {"LEGACY_HOST": "h"}
    result = deprecate(env, DEP_MAP)
    entry = result.deprecated[0]
    assert entry.replacement is None


def test_has_deprecated_true(mixed_env):
    result = deprecate(mixed_env, DEP_MAP)
    assert result.has_deprecated is True


def test_has_deprecated_false():
    result = deprecate({"SAFE_KEY": "value"}, DEP_MAP)
    assert result.has_deprecated is False


def test_summary_no_deprecated():
    result = deprecate({"SAFE_KEY": "value"}, DEP_MAP)
    assert result.summary() == "No deprecated keys found."


def test_summary_lists_deprecated(mixed_env):
    result = deprecate(mixed_env, DEP_MAP)
    summary = result.summary()
    assert "OLD_API_KEY" in summary
    assert "LEGACY_HOST" in summary
    assert "API_KEY" in summary  # replacement mentioned


def test_to_dict_shape():
    entry = DeprecationEntry(key="OLD", reason="Gone", replacement="NEW")
    d = entry.to_dict()
    assert d == {"key": "OLD", "reason": "Gone", "replacement": "NEW"}


def test_empty_env_no_deprecated():
    result = deprecate({}, DEP_MAP)
    assert not result.has_deprecated
    assert result.clean == []
