"""Tests for envdiff.annotator."""
import pytest
from envdiff.annotator import annotate, keys_by_tag, secret_keys, blank_keys


@pytest.fixture()
def env():
    return {
        "API_KEY": "abc123",
        "DB_PASSWORD": "",
        "APP_URL": "https://example.com",
        "PORT": "8080",
        "APP_NAME": "myapp",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_secret_tag_on_key(env):
    a = annotate(env)
    assert "secret" in a["API_KEY"]
    assert "secret" in a["DB_PASSWORD"]
    assert "secret" in a["AUTH_TOKEN"]


def test_no_secret_tag_on_plain(env):
    a = annotate(env)
    assert "secret" not in a["APP_NAME"]
    assert "secret" not in a["PORT"]


def test_blank_tag(env):
    a = annotate(env)
    assert "blank" in a["DB_PASSWORD"]
    assert "blank" not in a["API_KEY"]


def test_url_tag(env):
    a = annotate(env)
    assert "url" in a["APP_URL"]
    assert "url" not in a["APP_NAME"]


def test_numeric_tag(env):
    a = annotate(env)
    assert "numeric" in a["PORT"]
    assert "numeric" not in a["APP_NAME"]


def test_keys_by_tag(env):
    a = annotate(env)
    urls = keys_by_tag(a, "url")
    assert urls == ["APP_URL"]


def test_secret_keys_helper(env):
    sk = secret_keys(env)
    assert "API_KEY" in sk
    assert "AUTH_TOKEN" in sk
    assert "APP_NAME" not in sk


def test_blank_keys_helper(env):
    bk = blank_keys(env)
    assert bk == ["DB_PASSWORD"]
