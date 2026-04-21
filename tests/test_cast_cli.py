"""Tests for envdiff.cast_cli."""
import json
import os
import tempfile
import pytest

from envdiff.cast_cli import run


@pytest.fixture
def env_file():
    content = (
        "PORT=9000\n"
        "DEBUG=false\n"
        "RATIO=2.71\n"
        "APP_NAME=myservice\n"
        "EMPTY=\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


def _run(argv):
    return run(argv)


def test_exit_zero_on_valid_file(env_file):
    assert _run([env_file]) == 0


def test_exit_one_on_missing_file():
    assert _run(["/nonexistent/path/.env"]) == 1


def test_text_output_shows_types(env_file, capsys):
    _run([env_file])
    out = capsys.readouterr().out
    assert "PORT" in out
    assert "int" in out
    assert "DEBUG" in out
    assert "bool" in out


def test_text_output_shows_summary(env_file, capsys):
    _run([env_file])
    out = capsys.readouterr().out
    assert "keys cast" in out


def test_json_output_is_valid(env_file, capsys):
    _run([env_file, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "types" in data
    assert "values" in data
    assert data["file"] == env_file


def test_json_output_contains_all_keys(env_file, capsys):
    _run([env_file, "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert set(data["types"].keys()) == {"PORT", "DEBUG", "RATIO", "APP_NAME", "EMPTY"}


def test_json_type_inference_correct(env_file, capsys):
    _run([env_file, "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data["types"]["PORT"] == "int"
    assert data["types"]["DEBUG"] == "bool"
    assert data["types"]["RATIO"] == "float"
    assert data["types"]["APP_NAME"] == "str"
    assert data["types"]["EMPTY"] == "empty"
