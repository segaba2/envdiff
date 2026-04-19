"""Tests for envdiff.auditor."""
import json
from pathlib import Path

import pytest

from envdiff.auditor import AuditEntry, AuditLog, append_to_log, record
from envdiff.comparator import DiffResult


@pytest.fixture
def clean_result():
    return DiffResult(missing_in_a=set(), missing_in_b=set(), mismatched=set(), common=frozenset({"A", "B"}))


@pytest.fixture
def diff_result():
    return DiffResult(
        missing_in_a={"X"},
        missing_in_b={"Y"},
        mismatched={"Z"},
        common=frozenset({"Z"}),
    )


def test_record_creates_entry(diff_result):
    entry = record(diff_result, "a.env", "b.env", tag="ci")
    assert entry.file_a == "a.env"
    assert entry.file_b == "b.env"
    assert entry.missing_in_a == ["X"]
    assert entry.missing_in_b == ["Y"]
    assert entry.mismatched == ["Z"]
    assert entry.tag == "ci"
    assert entry.timestamp  # non-empty


def test_record_no_tag(clean_result):
    entry = record(clean_result, "a.env", "b.env")
    assert entry.tag is None
    assert entry.missing_in_a == []


def test_entry_roundtrip(diff_result):
    entry = record(diff_result, "a.env", "b.env", tag="prod")
    restored = AuditEntry.from_dict(entry.to_dict())
    assert restored.file_a == entry.file_a
    assert restored.mismatched == entry.mismatched
    assert restored.tag == "prod"


def test_audit_log_add_and_save(tmp_path, diff_result):
    log_path = tmp_path / "audit.json"
    entry = record(diff_result, "a.env", "b.env")
    log = append_to_log(log_path, entry)
    assert len(log.entries) == 1
    data = json.loads(log_path.read_text())
    assert len(data["entries"]) == 1


def test_audit_log_appends(tmp_path, diff_result, clean_result):
    log_path = tmp_path / "audit.json"
    append_to_log(log_path, record(diff_result, "a.env", "b.env"))
    append_to_log(log_path, record(clean_result, "x.env", "y.env"))
    log = AuditLog.load(log_path)
    assert len(log.entries) == 2


def test_audit_log_roundtrip(tmp_path, diff_result):
    log_path = tmp_path / "audit.json"
    entry = record(diff_result, "a.env", "b.env", tag="staging")
    log = AuditLog(entries=[entry])
    log.save(log_path)
    loaded = AuditLog.load(log_path)
    assert loaded.entries[0].tag == "staging"
    assert loaded.entries[0].missing_in_b == ["Y"]
