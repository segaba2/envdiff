"""Tests for envdiff.summarizer."""
import json
from pathlib import Path

import pytest

from envdiff.summarizer import summarize, SummaryReport, FileSummary


@pytest.fixture()
def env_files(tmp_path: Path):
    a = tmp_path / "a.env"
    a.write_text(
        "DB_HOST=localhost\n"
        "DB_PASSWORD=secret123\n"
        "EMPTY_VAL=\n"
        "API_KEY=abc\n"
    )
    b = tmp_path / "b.env"
    b.write_text(
        "APP_NAME=myapp\n"
        "SECRET_TOKEN=tok\n"
    )
    return [str(a), str(b)]


def test_total_files(env_files):
    report = summarize(env_files)
    assert report.total_files == 2


def test_total_keys(env_files):
    report = summarize(env_files)
    assert report.total_keys == 6  # 4 + 2


def test_blank_keys_counted(env_files):
    report = summarize(env_files)
    assert report.total_blank == 1


def test_secret_keys_counted(env_files):
    report = summarize(env_files)
    # DB_PASSWORD and API_KEY and SECRET_TOKEN should be flagged
    assert report.total_secrets >= 2


def test_file_summary_entries(env_files):
    report = summarize(env_files)
    assert len(report.files) == 2
    assert all(isinstance(fs, FileSummary) for fs in report.files)


def test_summary_string(env_files):
    report = summarize(env_files)
    text = report.summary()
    assert "Files analysed" in text
    assert "Total keys" in text
    assert "blank" in text


def test_to_dict_structure(env_files):
    report = summarize(env_files)
    d = report.to_dict()
    assert "total_files" in d
    assert "files" in d
    assert isinstance(d["files"], list)
    assert len(d["files"]) == 2


def test_to_dict_serialisable(env_files):
    report = summarize(env_files)
    # should not raise
    json.dumps(report.to_dict())


def test_empty_file_list():
    report = summarize([])
    assert report.total_files == 0
    assert report.total_keys == 0
    assert "Files analysed : 0" in report.summary()
