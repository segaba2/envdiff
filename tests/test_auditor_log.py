"""Additional unit tests for AuditLog helpers."""
import json
from pathlib import Path

import pytest

from envdiff.auditor import AuditEntry, AuditLog


def _make_entry(**kwargs) -> AuditEntry:
    defaults = dict(
        timestamp="2024-01-01T00:00:00+00:00",
        file_a="a.env",
        file_b="b.env",
        missing_in_a=[],
        missing_in_b=[],
        mismatched=[],
        tag=None,
    )
    defaults.update(kwargs)
    return AuditEntry(**defaults)


def test_log_to_dict_empty():
    log = AuditLog()
    assert log.to_dict() == {"entries": []}


def test_log_from_dict_empty():
    log = AuditLog.from_dict({"entries": []})
    assert log.entries == []


def test_log_save_creates_valid_json(tmp_path):
    log = AuditLog(entries=[_make_entry(tag="x")])
    p = tmp_path / "log.json"
    log.save(p)
    data = json.loads(p.read_text())
    assert data["entries"][0]["tag"] == "x"


def test_log_load_missing_entries_key(tmp_path):
    p = tmp_path / "log.json"
    p.write_text(json.dumps({}))
    log = AuditLog.load(p)
    assert log.entries == []


def test_entry_to_dict_keys():
    e = _make_entry(missing_in_b=["KEY"])
    d = e.to_dict()
    assert set(d.keys()) == {"timestamp", "file_a", "file_b", "missing_in_a", "missing_in_b", "mismatched", "tag"}
    assert d["missing_in_b"] == ["KEY"]
