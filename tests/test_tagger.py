import pytest
from envdiff.tagger import tag, tag_from_presets, TagResult


@pytest.fixture
def env():
    return {
        "DB_PASSWORD": "secret",
        "APP_URL": "https://example.com",
        "DEBUG": "true",
        "APP_NAME": "myapp",
        "API_KEY": "abc123",
        "DATABASE_HOST": "localhost",
    }


def test_tag_applies_single_rule(env):
    result = tag(env, {"secret": ["*PASSWORD*"]})
    assert "DB_PASSWORD" in result.tags
    assert "secret" in result.tags["DB_PASSWORD"]


def test_tag_unmatched_key_excluded(env):
    result = tag(env, {"secret": ["*PASSWORD*"]})
    assert "APP_NAME" not in result.tags


def test_tag_multiple_tags_on_one_key(env):
    result = tag(env, {
        "secret": ["*PASSWORD*"],
        "db": ["DB_*"],
    })
    assert result.tags["DB_PASSWORD"] == {"secret", "db"}


def test_keys_for_tag(env):
    result = tag(env, {"secret": ["*PASSWORD*", "*KEY*"]})
    keys = result.keys_for_tag("secret")
    assert "DB_PASSWORD" in keys
    assert "API_KEY" in keys


def test_tags_for_key_missing_returns_empty(env):
    result = tag(env, {"secret": ["*PASSWORD*"]})
    assert result.tags_for_key("APP_NAME") == set()


def test_rules_count(env):
    result = tag(env, {"a": ["*"], "b": ["APP_*"]})
    assert result.rules == 2


def test_summary_string(env):
    result = tag(env, {"secret": ["*PASSWORD*"]})
    s = result.summary()
    assert "keys tagged" in s
    assert "rules applied" in s


def test_tag_from_presets_secret(env):
    result = tag_from_presets(env)
    assert "secret" in result.tags_for_key("DB_PASSWORD")
    assert "secret" in result.tags_for_key("API_KEY")


def test_tag_from_presets_url(env):
    result = tag_from_presets(env)
    assert "url" in result.tags_for_key("APP_URL")


def test_tag_from_presets_extra_rules(env):
    result = tag_from_presets(env, extra_rules={"app": ["APP_*"]})
    assert "app" in result.tags_for_key("APP_NAME")
    assert "app" in result.tags_for_key("APP_URL")


def test_tag_from_presets_database(env):
    result = tag_from_presets(env)
    assert "database" in result.tags_for_key("DATABASE_HOST")
