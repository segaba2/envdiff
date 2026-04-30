"""CLI entry-point for the graph-diff feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.differ_graph import build_graph


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-graph",
        description="Compare every pair of .env files and show a diff graph.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--isolated",
        action="store_true",
        help="List files that have no differences with any other file.",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    missing = [f for f in args.files if not Path(f).is_file()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}", file=sys.stderr)
        return 1

    if len(args.files) < 2:
        print("error: at least two files are required", file=sys.stderr)
        return 1

    result = build_graph(args.files)

    if args.format == "json":
        payload = {
            "summary": result.summary(),
            "any_diff": result.any_diff(),
            "isolated": result.isolated_files(),
            "edges": [e.to_dict() for e in result.edges],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        for edge in result.edges:
            if edge.has_diff():
                print(f"  {edge.file_a} <-> {edge.file_b}")
                for k in edge.missing_in_a:
                    print(f"    - missing in {edge.file_a}: {k}")
                for k in edge.missing_in_b:
                    print(f"    - missing in {edge.file_b}: {k}")
                for k in edge.mismatches:
                    print(f"    ~ mismatch: {k}")
        if args.isolated:
            iso = result.isolated_files()
            print(f"isolated ({len(iso)}): {', '.join(iso) if iso else 'none'}")

    return 1 if result.any_diff() else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
