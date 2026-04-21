"""Integration tests: parse a real .env file then interpolate."""

import pytest
from envdiff.parser import parse_env_file
from envdiff.interpolator import interpolate


@pytest.fixture
def env_file(tmp_path):
    def _write(content: str):
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def test_parse_then_interpolate_chain(env_file):
    path = env_file(
        "ROOT=/opt/app\n"
        "DATA=$ROOT/data\n"
        "LOGS=$DATA/logs\n"
    )
    env = parse_env_file(path)
    result = interpolate(env)
    assert result.env["DATA"] == "/opt/app/data"
    assert result.env["LOGS"] == "/opt/app/data/logs"
    assert not result.has_unresolved


def test_parse_then_interpolate_unresolved(env_file):
    path = env_file("URL=https://$HOST/api\n")
    env = parse_env_file(path)
    result = interpolate(env)
    assert result.has_unresolved
    assert "URL" in result.unresolved


def test_quoted_values_interpolated(env_file):
    path = env_file('PREFIX="/usr"\nBIN="$PREFIX/bin"\n')
    env = parse_env_file(path)
    result = interpolate(env)
    assert result.env["BIN"] == "/usr/bin"


def test_no_references_all_plain(env_file):
    path = env_file("KEY1=alpha\nKEY2=beta\nKEY3=gamma\n")
    env = parse_env_file(path)
    result = interpolate(env)
    assert result.resolved == []
    assert result.unresolved == []
    assert result.env == env


def test_partial_resolution(env_file):
    path = env_file(
        "KNOWN=world\n"
        "GREETING=hello $KNOWN\n"
        "BROKEN=bye $UNKNOWN\n"
    )
    env = parse_env_file(path)
    result = interpolate(env)
    assert result.env["GREETING"] == "hello world"
    assert "BROKEN" in result.unresolved
    assert "GREETING" in result.resolved
