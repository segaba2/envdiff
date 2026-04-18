"""Tests for envdiff.validator."""
import pytest

from envdiff.validator import ValidationResult, validate, validate_from_template


@pytest.fixture
def base_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_valid_when_all_required_present(base_env):
    result = validate(base_env, {"HOST", "PORT", "DEBUG"})
    assert result.is_valid


def test_missing_key_detected(base_env):
    result = validate(base_env, {"HOST", "PORT", "DEBUG", "SECRET_KEY"})
    assert not result.is_valid
    assert "SECRET_KEY" in result.missing


def test_extra_keys_ignored_by_default(base_env):
    result = validate(base_env, {"HOST"})
    assert result.is_valid
    assert result.extra == []


def test_extra_keys_flagged_when_disallowed(base_env):
    result = validate(base_env, {"HOST"}, allow_extra=False)
    assert not result.is_valid
    assert "PORT" in result.extra
    assert "DEBUG" in result.extra


def test_empty_env_all_missing():
    result = validate({}, {"A", "B"})
    assert sorted(result.missing) == ["A", "B"]


def test_empty_required_always_valid(base_env):
    result = validate(base_env, set())
    assert result.is_valid


def test_summary_no_issues():
    result = ValidationResult()
    assert result.summary() == "All keys valid."


def test_summary_with_missing():
    result = ValidationResult(missing=["FOO", "BAR"])
    assert "Missing keys" in result.summary()
    assert "FOO" in result.summary()


def test_summary_with_extra():
    result = ValidationResult(extra=["EXTRA_KEY"])
    assert "Extra keys" in result.summary()


def test_validate_from_template():
    template = {"HOST": "", "PORT": "", "SECRET": ""}
    env = {"HOST": "localhost", "PORT": "5432"}
    result = validate_from_template(env, template)
    assert "SECRET" in result.missing
    assert result.extra == []


def test_validate_from_template_no_extra_allowed():
    template = {"HOST": ""}
    env = {"HOST": "localhost", "EXTRA": "value"}
    result = validate_from_template(env, template, allow_extra=False)
    assert "EXTRA" in result.extra
