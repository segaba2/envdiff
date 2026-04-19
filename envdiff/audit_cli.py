"""CLI sub-command: envdiff audit — record diffs to an audit log."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.auditor import append_to_log, record
from envdiff.differ import diff_files


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    desc = "Record a diff between two .env files into an audit log."
    if parent is not None:
        p = parent.add_parser("audit", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envdiff audit", description=desc)
    p.add_argument("file_a", help="First .env file")
    p.add_argument("file_b", help="Second .env file")
    p.add_argument("--log", default="envdiff_audit.json", help="Path to audit log (default: envdiff_audit.json)")
    p.add_argument("--tag", default=None, help="Optional label for this audit entry")
    p.add_argument("--exclude", nargs="*", default=[], metavar="PATTERN", help="Keys to exclude")
    p.add_argument("--prefix", default=None, help="Only compare keys with this prefix")
    return p


def run(args: argparse.Namespace) -> int:
    try:
        result = diff_files(
            args.file_a,
            args.file_b,
            exclude=args.exclude,
            prefix=args.prefix,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    entry = record(result, args.file_a, args.file_b, tag=args.tag)
    log_path = Path(args.log)
    log = append_to_log(log_path, entry)
    n = len(log.entries)
    print(f"Audit entry recorded ({n} total) → {log_path}")
    if result.missing_in_a or result.missing_in_b or result.mismatched:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    sys.exit(run(parser.parse_args()))


if __name__ == "__main__":  # pragma: no cover
    main()
