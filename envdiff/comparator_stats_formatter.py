"""Format ComparatorStats for display."""
from __future__ import annotations

import json
from typing import List

from envdiff.comparator_stats import ComparatorStats

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_text(stats: ComparatorStats, color: bool = True) -> str:
    lines: List[str] = []
    lines.append("=== Comparator Stats ===")
    lines.append(f"  Pairs evaluated : {stats.total_pairs}")
    lines.append(
        f"  Clean pairs     : "
        + _color(str(stats.clean_pairs), _GREEN, color)
    )
    lines.append(
        f"  Dirty pairs     : "
        + _color(str(stats.dirty_pairs), _RED if stats.dirty_pairs else _GREEN, color)
    )
    lines.append(f"  Missing in A    : {stats.total_missing_a}")
    lines.append(f"  Missing in B    : {stats.total_missing_b}")
    lines.append(f"  Mismatches      : {stats.total_mismatches}")
    rate_str = f"{stats.diff_rate:.0%}"
    rate_colored = _color(
        rate_str,
        _RED if stats.diff_rate > 0 else _GREEN,
        color,
    )
    lines.append(f"  Diff rate       : {rate_colored}")
    if stats.labels:
        lines.append("  Pairs:")
        for lbl in stats.labels:
            lines.append(f"    - {lbl}")
    return "\n".join(lines)


def format_json(stats: ComparatorStats) -> str:
    data = {
        "total_pairs": stats.total_pairs,
        "clean_pairs": stats.clean_pairs,
        "dirty_pairs": stats.dirty_pairs,
        "total_missing_a": stats.total_missing_a,
        "total_missing_b": stats.total_missing_b,
        "total_mismatches": stats.total_mismatches,
        "diff_rate": round(stats.diff_rate, 4),
        "labels": stats.labels,
    }
    return json.dumps(data, indent=2)
