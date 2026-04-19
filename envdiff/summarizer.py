"""summarizer.py – produce a human-readable summary across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.profiler import profile_file, ProfileResult


@dataclass
class FileSummary:
    path: str
    total_keys: int
    blank_keys: int
    secret_keys: int
    duplicate_values: int

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "total_keys": self.total_keys,
            "blank_keys": self.blank_keys,
            "secret_keys": self.secret_keys,
            "duplicate_values": self.duplicate_values,
        }


@dataclass
class SummaryReport:
    files: List[FileSummary] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_keys(self) -> int:
        return sum(f.total_keys for f in self.files)

    @property
    def total_blank(self) -> int:
        return sum(f.blank_keys for f in self.files)

    @property
    def total_secrets(self) -> int:
        return sum(f.secret_keys for f in self.files)

    def summary(self) -> str:
        lines = [f"Files analysed : {self.total_files}"]
        lines.append(f"Total keys     : {self.total_keys}")
        lines.append(f"Blank values   : {self.total_blank}")
        lines.append(f"Secret keys    : {self.total_secrets}")
        for fs in self.files:
            lines.append(
                f"  {fs.path}: {fs.total_keys} keys, "
                f"{fs.blank_keys} blank, {fs.secret_keys} secret, "
                f"{fs.duplicate_values} dup-values"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "total_keys": self.total_keys,
            "total_blank": self.total_blank,
            "total_secrets": self.total_secrets,
            "files": [f.to_dict() for f in self.files],
        }


def summarize(paths: List[str]) -> SummaryReport:
    """Build a SummaryReport from a list of .env file paths."""
    report = SummaryReport()
    for path in paths:
        pr: ProfileResult = profile_file(path)
        fs = FileSummary(
            path=path,
            total_keys=pr.total_keys,
            blank_keys=pr.blank_values,
            secret_keys=len(pr.likely_secrets),
            duplicate_values=len(pr.duplicate_values),
        )
        report.files.append(fs)
    return report
