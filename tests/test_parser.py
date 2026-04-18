"""Tests for envdiff.parser module."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError


def write_env(tmp_path: Path, content: str) -> Path:
    f = tmp_path / ".env"
    f.write_text(content, encoding="utf-8")
    return f


def test_basic_key_value(tmp_path):
    f = write_env(tmp_path, "DB_HOST=localhost\nDB_PORT=5432\n")
    result = parse_env_file(f)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_ignores_comments_and_blanks(tmp_path):
    content = "# this is a comment\n\nAPP_ENV=production\n"
    f = write_env(tmp_path, content)
    result = parse_env_file(f)
    assert result == {"APP_ENV": "production"}


def test_value_without_quotes(tmp_path):
    f = write_env(tmp_path, "SECRET=mysecret\n")
    assert parse_env_file(f)["SECRET"] == "mysecret"


def test_value_with_double_quotes(tmp_path):
    f = write_env(tmp_path, 'API_KEY="abc123"\n')
    assert parse_env_file(f)["API_KEY"] == "abc123"


def test_value_with_single_quotes(tmp_path):
    f = write_env(tmp_path, "TOKEN='xyz'\n")
    assert parse_env_file(f)["TOKEN"] == "xyz"


def test_empty_value_returns_none(tmp_path):
    f = write_env(tmp_path, "EMPTY=\n")
    assert parse_env_file(f)["EMPTY"] is None


def test_key_only_returns_none(tmp_path):
    f = write_env(tmp_path, "STANDALONE_KEY\n")
    assert parse_env_file(f)["STANDALONE_KEY"] is None


def test_file_not_found_raises():
    with pytest.raises(EnvParseError, match="File not found"):
        parse_env_file("/nonexistent/path/.env")


def test_invalid_key_raises(tmp_path):
    f = write_env(tmp_path, "INVALID-KEY=value\n")
    with pytest.raises(EnvParseError, match="Invalid key"):
        parse_env_file(f)


def test_multiple_equals_in_value(tmp_path):
    """Value containing '=' should be preserved."""
    f = write_env(tmp_path, "ENCODED=abc=def=ghi\n")
    assert parse_env_file(f)["ENCODED"] == "abc=def=ghi"


def test_inline_comment_stripped(tmp_path):
    """Unquoted values with inline comments should have the comment stripped."""
    f = write_env(tmp_path, "HOST=localhost # production host\n")
    assert parse_env_file(f)["HOST"] == "localhost"


def test_inline_comment_preserved_in_quoted_value(tmp_path):
    """Inline comments inside quoted values should be kept as part of the value."""
    f = write_env(tmp_path, 'DESCRIPTION="hello # world"\n')
    assert parse_env_file(f)["DESCRIPTION"] == "hello # world"
