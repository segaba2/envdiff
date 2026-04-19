import pytest
from envdiff.normalizer import normalize, NormalizeResult


@pytest.fixture
def sample():
    return {
        "db_host": "localhost",
        "db_pass": "'secret'",
        "api_url": 'https://example.com # production',
        "PORT": "8080",
    }


def test_uppercase_keys(sample):
    result = normalize(sample)
    assert "DB_HOST" in result.normalized
    assert "db_host" not in result.normalized


def test_uppercase_already_upper(sample):
    result = normalize(sample)
    assert "PORT" in result.normalized
    # no change recorded for PORT key itself
    key_changes = [c for c in result.changes if "'PORT'" in c and "->" in c]
    assert len(key_changes) == 0


def test_strip_single_quotes(sample):
    result = normalize(sample)
    assert result.normalized["DB_PASS"] == "secret"


def test_strip_inline_comment(sample):
    result = normalize(sample)
    assert result.normalized["API_URL"] == "https://example.com"


def test_no_changes_on_clean_env():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = normalize(env)
    assert result.normalized == env
    assert result.changes == []


def test_disable_uppercase():
    env = {"my_key": "value"}
    result = normalize(env, uppercase_keys=False)
    assert "my_key" in result.normalized
    assert "MY_KEY" not in result.normalized


def test_disable_strip_quotes():
    env = {"KEY": '"quoted"'}
    result = normalize(env, strip_quotes=False)
    assert result.normalized["KEY"] == '"quoted"'


def test_disable_inline_comment_strip():
    env = {"KEY": "value # comment"}
    result = normalize(env, strip_inline_comments=False)
    assert result.normalized["KEY"] == "value # comment"


def test_summary_no_changes():
    result = normalize({"HOST": "localhost"})
    assert result.summary() == "No normalization changes."


def test_summary_with_changes():
    env = {"key": "'val'"}
    result = normalize(env)
    assert "change" in result.summary()


def test_double_quotes_stripped():
    env = {"TOKEN": '"abc123"'}
    result = normalize(env)
    assert result.normalized["TOKEN"] == "abc123"
