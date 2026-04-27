"""Compute and compare MD5/SHA256 digests of .env files for integrity checking."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DigestResult:
    path: str
    sha256: str
    md5: str
    size: int

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "md5": self.md5,
            "size": self.size,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DigestResult":
        return cls(
            path=data["path"],
            sha256=data["sha256"],
            md5=data["md5"],
            size=data["size"],
        )


@dataclass
class DigestComparison:
    file_a: DigestResult
    file_b: DigestResult
    match: bool
    changed_algorithm: Optional[str] = None

    def summary(self) -> str:
        if self.match:
            return f"{self.file_a.path} and {self.file_b.path} are identical"
        return (
            f"{self.file_a.path} and {self.file_b.path} differ "
            f"(sha256: {self.file_a.sha256[:8]}... vs {self.file_b.sha256[:8]}...)"
        )


def digest_file(path: str | Path) -> DigestResult:
    """Return SHA256 and MD5 digests of the given file."""
    p = Path(path)
    raw = p.read_bytes()
    return DigestResult(
        path=str(p),
        sha256=hashlib.sha256(raw).hexdigest(),
        md5=hashlib.md5(raw).hexdigest(),
        size=len(raw),
    )


def compare_digests(path_a: str | Path, path_b: str | Path) -> DigestComparison:
    """Compare two files by their digests."""
    da = digest_file(path_a)
    db = digest_file(path_b)
    match = da.sha256 == db.sha256
    changed = None if match else "sha256"
    return DigestComparison(file_a=da, file_b=db, match=match, changed_algorithm=changed)


def save_digest(result: DigestResult, out_path: str | Path) -> None:
    """Persist a DigestResult to a JSON file."""
    Path(out_path).write_text(json.dumps(result.to_dict(), indent=2))


def load_digest(in_path: str | Path) -> DigestResult:
    """Load a previously saved DigestResult from a JSON file."""
    data = json.loads(Path(in_path).read_text())
    return DigestResult.from_dict(data)
