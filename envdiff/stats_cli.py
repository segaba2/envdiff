"""CLI entry-point: envdiff-stats — print aggregate diff statistics."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.differ import diff_files
from envdiff.differ_stats import compute_stats


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-stats",
        description="Compare multiple .env file pairs and show aggregate statistics.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Even number of files: pairs are (f1,f2), (f3,f4), …",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--exclude",
        metavar="PATTERN",
        action="append",
        default=[],
        help="Glob patterns for keys to exclude (repeatable).",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    paths = args.files
    if len(paths) % 2 != 0:
        print("error: provide an even number of files (pairs)", file=sys.stderr)
        return 2

    pairs = [(paths[i], paths[i + 1]) for i in range(0, len(paths), 2)]
    results = []
    for a, b in pairs:
        try:
            results.append(diff_files(a, b, exclude=args.exclude))
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    stats = compute_stats(results)

    if args.format == "json":
        data = {
            "total_pairs": stats.total_pairs,
            "pairs_with_diff": stats.pairs_with_diff,
            "pairs_clean": stats.pairs_clean,
            "total_missing_a": stats.total_missing_a,
            "total_missing_b": stats.total_missing_b,
            "total_mismatches": stats.total_mismatches,
            "diff_rate": round(stats.diff_rate, 4),
            "most_common_missing": stats.most_common_missing[:10],
        }
        print(json.dumps(data, indent=2))
    else:
        print(stats.summary())

    return 1 if stats.pairs_with_diff else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
