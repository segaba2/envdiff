"""CLI entry-point for the pin sub-command."""
from __future__ import annotations

import argparse
import sys

from envdiff.pinner import pin, load_pins


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-pin",
        description="Pin .env keys to a lockfile and report changes.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    save_p = sub.add_parser("save", help="Pin current .env to lockfile")
    save_p.add_argument("env", help="Path to .env file")
    save_p.add_argument("--lock", default=".env.lock", help="Lockfile path")
    save_p.add_argument("--quiet", action="store_true")

    show_p = sub.add_parser("show", help="Print contents of a lockfile")
    show_p.add_argument("--lock", default=".env.lock", help="Lockfile path")

    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "save":
        try:
            result = pin(args.env, args.lock)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        if not args.quiet:
            print(result.summary())

        return 1 if result.has_changes() else 0

    if args.cmd == "show":
        try:
            pins = load_pins(args.lock)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        if not pins:
            print("(no pinned keys)")
        else:
            for k, v in sorted(pins.items()):
                print(f"{k}={v}")
        return 0

    return 0  # unreachable


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
