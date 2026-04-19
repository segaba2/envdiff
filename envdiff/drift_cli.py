"""CLI entry point for the drift detection command."""
import argparse
import json
import sys
from envdiff.drifter import detect_drift_from_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-drift",
        description="Detect drift between a saved snapshot and a live .env file.",
    )
    p.add_argument("snapshot", help="Path to the saved snapshot JSON file.")
    p.add_argument("live", help="Path to the live .env file to compare against.")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return p


def run(args: argparse.Namespace) -> int:
    try:
        result = detect_drift_from_file(args.snapshot, args.live)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        out = {
            "snapshot_file": result.snapshot_file,
            "live_file": result.live_file,
            "added": result.added,
            "removed": result.removed,
            "changed": {k: {"old": v[0], "new": v[1]} for k, v in result.changed.items()},
            "has_drift": result.has_drift,
        }
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        for k in result.added:
            print(f"  + {k}  (new in live)")
        for k in result.removed:
            print(f"  - {k}  (removed from live)")
        for k, (old, new) in result.changed.items():
            print(f"  ~ {k}  '{old}' -> '{new}'")

    return 1 if result.has_drift else 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
