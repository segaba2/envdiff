"""Integration tests combining tagger with parser."""
import pytest
from pathlib import Path
from envdiff.parser import parse_env_file
from envdiff.tagger import tag, tag_from_presets


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "SECRET_KEY=abc\n"
        "DATABASE_URL=postgres://localhost/db\n"
        "REDIS_HOST=localhost\n"
        "LOG_LEVEL=info\n"
        "PORT=8080\n"
    )
    return p


def test_parse_and_tag_secret(env_file):
    env = parse_env_file(str(env_file))
    result = tag_from_presets(env)
    assert "secret" in result.tags_for_key("SECRET_KEY")


def test_parse_and_tag_database_url(env_file):
    env = parse_env_file(str(env_file))
    result = tag_from_presets(env)
    # DATABASE_URL matches both url and database presets
    tags = result.tags_for_key("DATABASE_URL")
    assert "url" in tags or "database" in tags


def test_untagged_key_not_in_result(env_file):
    env = parse_env_file(str(env_file))
    result = tag_from_presets(env)
    assert "PORT" not in result.tags


def test_custom_rule_via_extra(env_file):
    env = parse_env_file(str(env_file))
    result = tag_from_presets(env, extra_rules={"infra": ["REDIS_*", "PORT"]})
    assert "infra" in result.tags_for_key("REDIS_HOST")
    assert "infra" in result.tags_for_key("PORT")


def test_keys_for_tag_returns_sorted(env_file):
    env = parse_env_file(str(env_file))
    result = tag_from_presets(env)
    keys = result.keys_for_tag("url")
    assert keys == sorted(keys)
