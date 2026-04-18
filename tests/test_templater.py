"""Tests for envdiff.templater."""
from pathlib import Path

import pytest

from envdiff.templater import build_template, render_template, write_template


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "true",
        "SECRET_KEY": "supersecret",
        "DB_PASSWORD": "hunter2",
        "PORT": "8080",
        "EMPTY_VAR": "",
    }


def test_non_secret_values_preserved(sample_env):
    result = build_template(sample_env)
    assert result.output["APP_NAME"] == "myapp"
    assert result.output["PORT"] == "8080"
    assert result.output["DEBUG"] == "true"


def test_secret_values_blanked(sample_env):
    result = build_template(sample_env)
    assert result.output["SECRET_KEY"] == ""
    assert result.output["DB_PASSWORD"] == ""


def test_empty_values_stay_empty(sample_env):
    result = build_template(sample_env)
    assert result.output["EMPTY_VAR"] == ""


def test_all_keys_present(sample_env):
    result = build_template(sample_env)
    assert set(result.keys) == set(sample_env.keys())


def test_summary_string(sample_env):
    result = build_template(sample_env)
    assert "6" in result.summary()


def test_render_produces_key_equals_value(sample_env):
    result = build_template(sample_env)
    rendered = render_template(result)
    lines = rendered.strip().splitlines()
    assert all("=" in line for line in lines)


def test_render_ends_with_newline(sample_env):
    result = build_template(sample_env)
    rendered = render_template(result)
    assert rendered.endswith("\n")


def test_write_template_creates_file(tmp_path, sample_env):
    dest = tmp_path / ".env.example"
    result = write_template(sample_env, dest)
    assert dest.exists()
    content = dest.read_text()
    assert "APP_NAME=myapp" in content
    assert len(result.keys) == len(sample_env)


def test_empty_env_renders_empty_file(tmp_path):
    dest = tmp_path / ".env.example"
    result = write_template({}, dest)
    assert dest.read_text() == ""
    assert result.keys == []
