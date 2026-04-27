"""CLI entry-point for comparator-stats: aggregate diff statistics across many file pairs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

from envdiff.differ import diff_files
from envdiff.comparator_stats import compute_comparator_stats


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-comparator-stats",
        description="Aggregate diff statistics across multiple .env file pairs.",
    )
    p.add_argument(
        "pairs",
        nargs="+",
        metavar="A:B",
        help="Colon-separated file pairs, e.g. dev.env:prod.env",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def _parse_pairs(raw: List[str]) -> List[Tuple[Path, Path]]:
    pairs: List[Tuple[Path, Path]] = []
    for token in raw:
        if ":" not in token:
            raise SystemExit(f"Invalid pair (expected A:B): {token!r}")
        a, b = token.split(":", 1)
        pairs.append((Path(a), Path(b)))
    return pairs


def run(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pairs = _parse_pairs(args.pairs)
    results = []
    labels = []
    for a, b in pairs:
        results.append(diff_files(a, b))
        labels.append(f"{a}:{b}")

    stats = compute_comparator_stats(results, labels=labels)

    if args.format == "json":
        print(json.dumps({
            "total_pairs": stats.total_pairs,
            "clean_pairs": stats.clean_pairs,
            "dirty_pairs": stats.dirty_pairs,
            "total_missing_a": stats.total_missing_a,
            "total_missing_b": stats.total_missing_b,
            "total_mismatches": stats.total_mismatches,
            "diff_rate": round(stats.diff_rate, 4),
        }, indent=2))
    else:
        print(stats.summary())

    return 1 if stats.dirty_pairs > 0 else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
