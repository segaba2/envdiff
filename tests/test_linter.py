"""Tests for envdiff.linter."""
import pytest
from envdiff.linter import lint_lines, lint_file, LintResult


def issues_by_code(result: LintResult, code: str):
    return [i for i in result.issues if i.code == code]


def test_clean_file_no_issues():
    lines = ["DB_HOST=localhost\n", "DB_PORT=5432\n"]
    result = lint_lines(lines)
    assert result.ok


def test_trailing_whitespace_detected():
    lines = ["DB_HOST=localhost   \n"]
    result = lint_lines(lines)
    w001 = issues_by_code(result, 'W001')
    assert len(w001) == 1
    assert w001[0].line == 1


def test_missing_equals_separator():
    lines = ["BADLINE\n"]
    result = lint_lines(lines)
    e001 = issues_by_code(result, 'E001')
    assert len(e001) == 1


def test_lowercase_key_flagged():
    lines = ["db_host=localhost\n"]
    result = lint_lines(lines)
    w002 = issues_by_code(result,assert len(w002) == 1
    assert w002[0].key == 'db_host'


def test_uppercase_key_ok():
    lines = ["DB_HOST=localhost\n"]
    result = lint_lines(lines)
    assert not issues_by_code(result, 'W002')


def test_duplicate_key_detected():
    lines = ["DB_HOST=a\n", "DB_HOST=b\n"]
    result = lint_lines(lines)
    e002 = issues_by_code(result, 'E002')
    assert len(e002) == 1
    assert e002[0].line == 2


def test_value_surrounding_whitespace():
    lines = ["DB_HOST= localhost \n"]
    result = lint_lines(lines)
    w003 = issues_by_code(result, 'W003')
    assert len(w003) == 1


def test_comments_and_blanks_ignored():
    lines = ["# comment\n", "\n", "DB=val\n"]
    result = lint_lines(lines)
    assert result.ok


def test_summary_no_issues():
    result = lint_lines(["KEY=value\n"])
    assert result.summary() == "No lint issues found."


def test_summary_with_issues():
    result = lint_lines(["bad line\n"])
    s = result.summary()
    assert 'E001' in s
    assert 'lint issue' in s


def test_lint_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=ok\ndup=x\ndup=y\n")
    result = lint_file(str(f))
    assert not result.ok
