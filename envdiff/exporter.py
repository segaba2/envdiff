"""Export diff results to various file formats."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Literal

from envdiff.comparator import DiffResult

ExportFormat = Literal["json", "csv", "text"]


def export_json(result: DiffResult, path: Path) -> None:
    """Write diff result as JSON to *path*."""
    data = {
        "missing_in_a": sorted(result.missing_in_a),
        "missing_in_b": sorted(result.missing_in_b),
        "mismatched": [
            {"key": k, "a": v[0], "b": v[1]}
            for k, v in sorted(result.mismatched.items())
        ],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_csv(result: DiffResult, path: Path) -> None:
    """Write diff result as CSV to *path*.

    Columns: key, status, value_a, value_b
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "value_a", "value_b"])

    for key in sorted(result.missing_in_a):
        writer.writerow([key, "missing_in_a", "", ""])

    for key in sorted(result.missing_in_b):
        writer.writerow([key, "missing_in_b", "", ""])

    for key, (val_a, val_b) in sorted(result.mismatched.items()):
        writer.writerow([key, "mismatch", val_a, val_b])

    path.write_text(buf.getvalue(), encoding="utf-8")


def export_text(result: DiffResult, path: Path) -> None:
    """Write a plain-text summary to *path*."""
    lines: list[str] = []
    for key in sorted(result.missing_in_a):
        lines.append(f"MISSING_IN_A  {key}")
    for key in sorted(result.missing_in_b):
        lines.append(f"MISSING_IN_B  {key}")
    for key, (val_a, val_b) in sorted(result.mismatched.items()):
        lines.append(f"MISMATCH      {key}  [{val_a!r} != {val_b!r}]")
    if not lines:
        lines.append("No differences found.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export(result: DiffResult, path: Path, fmt: ExportFormat = "text") -> None:
    """Dispatch export to the appropriate formatter."""
    dispatch = {"json": export_json, "csv": export_csv, "text": export_text}
    if fmt not in dispatch:
        raise ValueError(f"Unsupported export format: {fmt!r}")
    dispatch[fmt](result, path)
