import json
import os
import pytest
from pathlib import Path
from envdiff.tag_cli import build_parser, run


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_PASSWORD=secret\n"
        "APP_URL=https://example.com\n"
        "APP_NAME=myapp\n"
        "DEBUG=true\n"
    )
    return str(p)


def _run(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


def test_exit_zero_on_valid_file(env_file):
    assert _run([env_file]) == 0


def test_exit_one_on_missing_file():
    assert _run(["nonexistent.env"]) == 1


def test_text_output_shows_tags(env_file, capsys):
    _run([env_file])
    out = capsys.readouterr().out
    assert "DB_PASSWORD" in out
    assert "secret" in out


def test_json_output_is_valid(env_file, capsys):
    _run([env_file, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, dict)


def test_json_output_contains_secret_key(env_file, capsys):
    _run([env_file, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DB_PASSWORD" in data
    assert "secret" in data["DB_PASSWORD"]


def test_filter_tag_limits_output(env_file, capsys):
    _run([env_file, "--tag", "url"])
    out = capsys.readouterr().out
    assert "APP_URL" in out
    assert "DB_PASSWORD" not in out


def test_filter_tag_no_match_message(env_file, capsys):
    _run([env_file, "--tag", "nonexistent"])
    out = capsys.readouterr().out
    assert "No tagged keys found" in out
