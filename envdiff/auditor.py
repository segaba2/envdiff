"""Audit trail: record and replay diffs with timestamps."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class AuditEntry:
    timestamp: str
    file_a: str
    file_b: str
    missing_in_a: List[str]
    missing_in_b: List[str]
    mismatched: List[str]
    tag: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "file_a": self.file_a,
            "file_b": self.file_b,
            "missing_in_a": self.missing_in_a,
            "missing_in_b": self.missing_in_b,
            "mismatched": self.mismatched,
            "tag": self.tag,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AuditEntry":
        return cls(**d)


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, d: dict) -> "AuditLog":
        return cls(entries=[AuditEntry.from_dict(e) for e in d.get("entries", [])])

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> "AuditLog":
        return cls.from_dict(json.loads(path.read_text()))


def record(result: DiffResult, file_a: str, file_b: str, tag: Optional[str] = None) -> AuditEntry:
    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        file_a=file_a,
        file_b=file_b,
        missing_in_a=sorted(result.missing_in_a),
        missing_in_b=sorted(result.missing_in_b),
        mismatched=sorted(result.mismatched),
        tag=tag,
    )


def append_to_log(log_path: Path, entry: AuditEntry) -> AuditLog:
    if log_path.exists():
        log = AuditLog.load(log_path)
    else:
        log = AuditLog()
    log.add(entry)
    log.save(log_path)
    return log
