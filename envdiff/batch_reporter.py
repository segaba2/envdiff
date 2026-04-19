"""Batch reporter: render MultiDiffResult to text or JSON."""
from __future__ import annotations
import json
from envdiff.differ_plus import MultiDiffResult


def render_text(result: MultiDiffResult, color: bool = False) -> str:
    lines = []
    for label, diff in result.pairs.items():
        lines.append(f"=== {label} ===")
        for key in diff.missing_in_a:
            lines.append(f"  [+A missing] {key}")
        for key in diff.missing_in_b:
            lines.append(f"  [+B missing] {key}")
        for key, (va, vb) in diff.mismatches.items():
            lines.append(f"  [mismatch]   {key}: {va!r} != {vb!r}")
        if not diff.has_diff():
            lines.append("  No differences.")
    return "\n".join(lines)


def render_json(result: MultiDiffResult) -> str:
    data = {}
    for label, diff in result.pairs.items():
        data[label] = {
            "missing_in_a": list(diff.missing_in_a),
            "missing_in_b": list(diff.missing_in_b),
            "mismatches": {k: list(v) for k, v in diff.mismatches.items()},
        }
    return json.dumps(data, indent=2)


def exit_code(result: MultiDiffResult) -> int:
    return 1 if result.any_diff() else 0
