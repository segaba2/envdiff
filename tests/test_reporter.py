"""Tests for envdiff.reporter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import exit_code, print_report, render, write_report


@pytest.fixture()
def clean() -> DiffResult:
    return DiffResult(missing_in_a=set(), missing_in_b=set(), mismatched={})


@pytest.fixture()
def dirty() -> DiffResult:
    return DiffResult(
        missing_in_a={"FOO"},
        missing_in_b={"BAR"},
        mismatched={"PORT": ("8080", "9090")},
    )


def test_render_text_no_diff(clean: DiffResult) -> None:
    out = render(clean, fmt="text", color=False)
    assert "No differences" in out


def test_render_text_diff(dirty: DiffResult) -> None:
    out = render(dirty, fmt="text", color=False)
    assert "FOO" in out
    assert "BAR" in out
    assert "PORT" in out


def test_render_json_is_valid(dirty: DiffResult) -> None:
    out = render(dirty, fmt="json")
    data = json.loads(out)
    assert "missing_in_a" in data
    assert "missing_in_b" in data
    assert "mismatched" in data


def test_exit_code_clean(clean: DiffResult) -> None:
    assert exit_code(clean) == 0


def test_exit_code_dirty(dirty: DiffResult) -> None:
    assert exit_code(dirty) == 1


def test_write_report_creates_file(tmp_path: Path, dirty: DiffResult) -> None:
    out_file = tmp_path / "report.txt"
    write_report(dirty, out_file, fmt="text")
    assert out_file.exists()
    content = out_file.read_text()
    assert "PORT" in content


def test_write_report_json(tmp_path: Path, dirty: DiffResult) -> None:
    out_file = tmp_path / "report.json"
    write_report(dirty, out_file, fmt="json")
    data = json.loads(out_file.read_text())
    assert data["mismatched"]["PORT"] == ["8080", "9090"]


def test_print_report_no_error(capsys: pytest.CaptureFixture, clean: DiffResult) -> None:
    print_report(clean, fmt="text", color=False)
    captured = capsys.readouterr()
    assert "No differences" in captured.out
