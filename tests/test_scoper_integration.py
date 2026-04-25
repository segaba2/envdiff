"""Integration tests: parse a real .env file then apply scope filtering."""
from pathlib import Path
import pytest
from envdiff.parser import parse_env_file
from envdiff.scoper import scope


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "APP_DEBUG=true\n"
        "APP_SECRET=topsecret\n"
        "DB_URL=postgres://localhost/mydb\n"
        "DB_POOL=5\n"
        "REDIS_URL=redis://localhost\n"
    )
    return p


def test_parse_then_scope_app(env_file):
    env = parse_env_file(env_file)
    result = scope(env, "app")
    assert set(result.matched.keys()) == {"APP_NAME", "APP_DEBUG", "APP_SECRET"}


def test_parse_then_scope_db(env_file):
    env = parse_env_file(env_file)
    result = scope(env, "db")
    assert "DB_URL" in result.matched
    assert "DB_POOL" in result.matched


def test_strip_prefix_integration(env_file):
    env = parse_env_file(env_file)
    result = scope(env, "app", strip_prefix=True)
    assert "NAME" in result.matched
    assert "DEBUG" in result.matched
    assert result.matched["NAME"] == "myapp"


def test_multi_prefix_integration(env_file):
    env = parse_env_file(env_file)
    result = scope(env, "backend", prefixes=["DB_", "REDIS_"])
    assert "DB_URL" in result.matched
    assert "REDIS_URL" in result.matched
    assert "APP_NAME" in result.excluded


def test_excluded_count_correct(env_file):
    env = parse_env_file(env_file)
    result = scope(env, "app")
    assert len(result.matched) + len(result.excluded) == len(env)
