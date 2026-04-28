"""Tests for envdiff.cloner and envdiff.clone_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.cloner import clone, clone_to_file, CloneResult


@pytest.fixture()
def base_env() -> dict[str, str]:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "secret123",
        "DEBUG": "true",
        "API_KEY": "abc",
    }


# ---------------------------------------------------------------------------
# clone()
# ---------------------------------------------------------------------------

def test_returns_clone_result(base_env):
    result = clone(base_env, source=".env", target=".env.prod")
    assert isinstance(result, CloneResult)


def test_all_keys_copied(base_env):
    result = clone(base_env, source=".env", target=".env.prod")
    assert set(result.env.keys()) == set(base_env.keys())


def test_values_preserved_when_no_overrides(base_env):
    result = clone(base_env, source=".env", target=".env.prod")
    assert result.env["APP_NAME"] == "myapp"
    assert result.env["DEBUG"] == "true"


def test_override_replaces_value(base_env):
    result = clone(base_env, source=".env", target=".env.prod",
                   overrides={"APP_NAME": "prodapp"})
    assert result.env["APP_NAME"] == "prodapp"
    assert "APP_NAME" in result.overridden


def test_override_introduces_new_key(base_env):
    result = clone(base_env, source=".env", target=".env.prod",
                   overrides={"NEW_KEY": "new_value"})
    assert result.env["NEW_KEY"] == "new_value"
    assert "NEW_KEY" in result.overridden


def test_mask_secrets_replaces_sensitive_values(base_env):
    result = clone(base_env, source=".env", target=".env.prod",
                   mask_secrets=True)
    # DB_PASSWORD and API_KEY look like secrets
    assert result.env["DB_PASSWORD"] == "CHANGE_ME"
    assert result.env["API_KEY"] == "CHANGE_ME"
    assert "DB_PASSWORD" in result.masked
    assert "API_KEY" in result.masked


def test_mask_secrets_preserves_non_sensitive(base_env):
    result = clone(base_env, source=".env", target=".env.prod",
                   mask_secrets=True)
    assert result.env["APP_NAME"] == "myapp"
    assert result.env["DEBUG"] == "true"


def test_custom_placeholder(base_env):
    result = clone(base_env, source=".env", target=".env.prod",
                   mask_secrets=True, mask_placeholder="__REDACTED__")
    assert result.env["DB_PASSWORD"] == "__REDACTED__"


def test_override_takes_priority_over_mask(base_env):
    result = clone(base_env, source=".env", target=".env.prod",
                   overrides={"DB_PASSWORD": "explicit"},
                   mask_secrets=True)
    assert result.env["DB_PASSWORD"] == "explicit"
    assert "DB_PASSWORD" in result.overridden
    assert "DB_PASSWORD" not in result.masked


def test_summary_contains_key_count(base_env):
    result = clone(base_env, source=".env", target=".env.prod")
    assert f"keys={len(base_env)}" in result.summary()


# ---------------------------------------------------------------------------
# clone_to_file()
# ---------------------------------------------------------------------------

def test_clone_to_file_creates_file(tmp_path, base_env):
    target = tmp_path / ".env.prod"
    clone_to_file(base_env, source=".env", target=target)
    assert target.exists()


def test_clone_to_file_written_content(tmp_path, base_env):
    target = tmp_path / ".env.prod"
    clone_to_file(base_env, source=".env", target=target)
    text = target.read_text()
    assert "APP_NAME=myapp" in text
    assert "DEBUG=true" in text


def test_clone_to_file_with_mask(tmp_path, base_env):
    target = tmp_path / ".env.prod"
    clone_to_file(base_env, source=".env", target=target, mask_secrets=True)
    text = target.read_text()
    assert "DB_PASSWORD=CHANGE_ME" in text


# ---------------------------------------------------------------------------
# clone_cli via subprocess-style invocation
# ---------------------------------------------------------------------------

def test_cli_exit_zero(tmp_path):
    from envdiff.clone_cli import run
    src = tmp_path / ".env"
    src.write_text("APP=hello\nDEBUG=false\n")
    dst = tmp_path / ".env.prod"
    code = run([str(src), str(dst)])
    assert code == 0
    assert dst.exists()


def test_cli_exit_one_missing_source(tmp_path):
    from envdiff.clone_cli import run
    code = run([str(tmp_path / "missing.env"), str(tmp_path / "out.env")])
    assert code == 1


def test_cli_set_override(tmp_path):
    from envdiff.clone_cli import run
    src = tmp_path / ".env"
    src.write_text("APP=hello\n")
    dst = tmp_path / ".env.prod"
    run([str(src), str(dst), "--set", "APP=world"])
    assert "APP=world" in dst.read_text()


def test_cli_mask_secrets(tmp_path):
    from envdiff.clone_cli import run
    src = tmp_path / ".env"
    src.write_text("API_KEY=supersecret\nAPP=hello\n")
    dst = tmp_path / ".env.prod"
    run([str(src), str(dst), "--mask-secrets"])
    assert "CHANGE_ME" in dst.read_text()
