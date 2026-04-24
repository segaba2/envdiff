"""Tests for envdiff.classifier."""

from __future__ import annotations

import pytest

from envdiff.classifier import ClassifyResult, classify, _classify_key


@pytest.fixture()
def sample() -> dict[str, str]:
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "DB_PASSWORD": "s3cr3t",
        "API_TOKEN": "tok_abc123",
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DEBUG": "true",
        "LOG_FILE": "/var/log/app.log",
        "ADMIN_EMAIL": "admin@example.com",
        "REQUEST_TIMEOUT": "30",
        "APP_NAME": "envdiff",
    }


def test_returns_classify_result(sample):
    result = classify(sample)
    assert isinstance(result, ClassifyResult)


def test_all_keys_classified(sample):
    result = classify(sample)
    assert set(result.categories.keys()) == set(sample.keys())


def test_secret_category_detected(sample):
    result = classify(sample)
    assert result.categories["DB_PASSWORD"] == "secret"
    assert result.categories["API_TOKEN"] == "secret"


def test_database_category_detected(sample):
    result = classify(sample)
    assert result.categories["DATABASE_URL"] == "database"


def test_url_category_detected(sample):
    result = classify(sample)
    assert result.categories["APP_HOST"] == "url"


def test_port_category_detected(sample):
    result = classify(sample)
    assert result.categories["APP_PORT"] == "port"


def test_flag_category_detected(sample):
    result = classify(sample)
    assert result.categories["DEBUG"] == "flag"


def test_path_category_detected(sample):
    result = classify(sample)
    assert result.categories["LOG_FILE"] == "path"


def test_email_category_detected(sample):
    result = classify(sample)
    assert result.categories["ADMIN_EMAIL"] == "email"


def test_timeout_category_detected(sample):
    result = classify(sample)
    assert result.categories["REQUEST_TIMEOUT"] == "timeout"


def test_general_fallback(sample):
    result = classify(sample)
    assert result.categories["APP_NAME"] == "general"


def test_by_category_groups_correctly(sample):
    result = classify(sample)
    assert "DB_PASSWORD" in result.by_category["secret"]
    assert "API_TOKEN" in result.by_category["secret"]


def test_by_category_keys_sorted(sample):
    result = classify(sample)
    for keys in result.by_category.values():
        assert keys == sorted(keys)


def test_summary_string(sample):
    result = classify(sample)
    s = result.summary()
    assert "secret" in s
    assert "general" in s


def test_empty_env():
    result = classify({})
    assert result.categories == {}
    assert result.by_category == {}
    assert result.summary() == "No keys classified."


def test_classify_key_direct():
    assert _classify_key("MY_SECRET_KEY") == "secret"
    assert _classify_key("PLAIN") == "general"
