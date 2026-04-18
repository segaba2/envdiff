import pytest
from envdiff.scorer import score, ScoreReport, _grade
from envdiff.profiler import profile as run_profile
from envdiff.linter import lint_lines, LintResult, LintIssue


@pytest.fixture
def clean_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "envdiff"}


@pytest.fixture
def clean_profile(clean_env):
    return run_profile(clean_env)


@pytest.fixture
def clean_lint():
    lines = ["DB_HOST=localhost\n", "DB_PORT=5432\n", "APP_NAME=envdiff\n"]
    return lint_lines(lines)


def test_perfect_score(clean_env, clean_profile, clean_lint):
    report = score(clean_profile, clean_lint, clean_env)
    assert report.score == 100
    assert report.penalties == []


def test_empty_file_scores_zero():
    from envdiff.profiler import ProfileResult
    empty_profile = ProfileResult(total=0, blank_values=0, duplicate_values={})
    lint = LintResult(issues=[])
    report = score(empty_profile, lint, {})
    assert report.score == 0


def test_blank_values_penalised():
    env = {"A": "", "B": "", "C": "", "D": "val"}
    p = run_profile(env)
    lint = LintResult(issues=[])
    report = score(p, lint, env)
    assert report.score < 100
    assert any("blank" in pen for pen in report.penalties)


def test_lint_issues_penalised(clean_env, clean_profile):
    issues = [LintIssue(line=1, code="E001", message="bad") for _ in range(4)]
    bad_lint = LintResult(issues=issues)
    report = score(clean_profile, bad_lint, clean_env)
    assert report.score < 100
    assert any("lint" in pen for pen in report.penalties)


def test_blank_secret_penalised():
    env = {"SECRET_KEY": "", "APP": "ok"}
    p = run_profile(env)
    lint = LintResult(issues=[])
    report = score(p, lint, env)
    assert report.score < 100
    assert any("secret" in pen for pen in report.penalties)


def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(90) == "A"
    assert _grade(89) == "B"
    assert _grade(75) == "B"
    assert _grade(74) == "C"
    assert _grade(60) == "C"
    assert _grade(59) == "D"
    assert _grade(40) == "D"
    assert _grade(39) == "F"


def test_summary_contains_score(clean_env, clean_profile, clean_lint):
    report = score(clean_profile, clean_lint, clean_env)
    summary = report.summary()
    assert "100/100" in summary
    assert "(A)" in summary
