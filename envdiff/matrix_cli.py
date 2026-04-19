"""CLI entry-point for the matrix diff feature."""
from __future__ import annotations
import argparse
import json
import sys
from envdiff.differ_matrix import diff_matrix


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-matrix",
        description="Compare every pair of .env files in a set.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Two or more .env files")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    return p


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if len(args.files) < 2:
        print("error: at least two files required", file=sys.stderr)
        return 2

    matrix = diff_matrix(args.files)

    if args.fmt == "json":
        out: dict = {"summary": matrix.summary(), "pairs": []}
        for (a, b), r in matrix.cells.items():
            out["pairs"].append(
                {
                    "a": a,
                    "b": b,
                    "missing_in_a": list(r.missing_in_a),
                    "missing_in_b": list(r.missing_in_b),
                    "mismatches": list(r.mismatches),
                }
            )
        print(json.dumps(out, indent=2))
    else:
        print(matrix.summary())
        for (a, b), r in matrix.cells.items():
            if r.has_diff():
                print(f"\n  {a} vs {b}")
                for k in sorted(r.missing_in_b):
                    print(f"    - {k} missing in {b}")
                for k in sorted(r.missing_in_a):
                    print(f"    - {k} missing in {a}")
                for k in sorted(r.mismatches):
                    print(f"    ~ {k} value mismatch")

    return 1 if matrix.any_diff() else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
