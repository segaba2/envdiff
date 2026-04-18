"""CLI helpers for snapshot subcommands: take, diff."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff import snapshotter


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envdiff-snapshot", description="Snapshot .env files")
    sub = p.add_subparsers(dest="cmd", required=True)

    take_p = sub.add_parser("take", help="Capture a snapshot of an env file")
    take_p.add_argument("env_file", help="Path to .env file")
    take_p.add_argument("output", help="Path to write snapshot JSON")

    diff_p = sub.add_parser("diff", help="Diff two snapshots")
    diff_p.add_argument("old", help="Path to old snapshot JSON")
    diff_p.add_argument("new", help="Path to new snapshot JSON")
    diff_p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")

    return p


def run(args: argparse.Namespace) -> int:
    if args.cmd == "take":
        snap = snapshotter.take(args.env_file)
        snapshotter.save(snap, args.output)
        print(f"Snapshot saved: {snap.summary}")
        return 0

    if args.cmd == "diff":
        old = snapshotter.load(args.old)
        new = snapshotter.load(args.new)
        diff = snapshotter.diff_snapshots(old, new)
        if args.as_json:
            print(json.dumps(diff, indent=2))
        else:
            if not diff:
                print("No changes detected.")
            else:
                for key, info in diff.items():
                    print(f"{info['status'].upper():8s} {key}: {info['old']!r} -> {info['new']!r}")
        return 1 if diff else 0

    return 2


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
