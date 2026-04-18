"""Tests for envdiff.exporter."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export, export_csv, export_json, export_text


@pytest.fixture()
def clean() -> DiffResult:
    return DiffResult(missing_in_a=set(), missing_in_b=set(), mismatched={})


@pytest.fixture()
def dirty() -> DiffResult:
    return DiffResult(
        missing_in_a={"ONLY_IN_B"},
        missing_in_b={"ONLY_IN_A"},
        mismatched={"SHARED": ("old", "new")},
    )


def test_export_json_clean(tmp_path: Path, clean: DiffResult) -> None:
    out = tmp_path / "out.json"
    export_json(clean, out)
    data = json.loads(out.read_text())
    assert data["missing_in_a"] == []
    assert data["missing_in_b"] == []
    assert data["mismatched"] == []


def test_export_json_dirty(tmp_path: Path, dirty: DiffResult) -> None:
    out = tmp_path / "out.json"
    export_json(dirty, out)
    data = json.loads(out.read_text())
    assert "ONLY_IN_B" in data["missing_in_a"]
    assert "ONLY_IN_A" in data["missing_in_b"]
    assert data["mismatched"][0] == {"key": "SHARED", "a": "old", "b": "new"}


def test_export_csv_headers(tmp_path: Path, clean: DiffResult) -> None:
    out = tmp_path / "out.csv"
    export_csv(clean, out)
    rows = list(csv.reader(out.read_text().splitlines()))
    assert rows[0] == ["key", "status", "value_a", "value_b"]


def test_export_csv_dirty_rows(tmp_path: Path, dirty: DiffResult) -> None:
    out = tmp_path / "out.csv"
    export_csv(dirty, out)
    rows = list(csv.DictReader(out.read_text().splitlines()))
    statuses = {r["key"]: r["status"] for r in rows}
    assert statuses["ONLY_IN_B"] == "missing_in_a"
    assert statuses["ONLY_IN_A"] == "missing_in_b"
    assert statuses["SHARED"] == "mismatch"


def test_export_text_no_diff(tmp_path: Path, clean: DiffResult) -> None:
    out = tmp_path / "out.txt"
    export_text(clean, out)
    assert "No differences found." in out.read_text()


def test_export_text_diff(tmp_path: Path, dirty: DiffResult) -> None:
    out = tmp_path / "out.txt"
    export_text(dirty, out)
    content = out.read_text()
    assert "MISSING_IN_A" in content
    assert "MISSING_IN_B" in content
    assert "MISMATCH" in content


def test_export_dispatch(tmp_path: Path, dirty: DiffResult) -> None:
    for fmt in ("json", "csv", "text"):
        out = tmp_path / f"out.{fmt}"
        export(dirty, out, fmt=fmt)  # type: ignore[arg-type]
        assert out.exists()


def test_export_invalid_format(tmp_path: Path, clean: DiffResult) -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        export(clean, tmp_path / "x", fmt="xml")  # type: ignore[arg-type]
