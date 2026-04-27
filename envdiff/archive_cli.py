"""CLI entry-point for the archive / restore commands."""

from __future__ import annotations

import argparse
import sys

from envdiff.archiver import archive, restore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-archive",
        description="Archive or restore .env files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pack = sub.add_parser("pack", help="Pack env files into a zip archive")
    pack.add_argument("files", nargs="+", help=".env files to archive")
    pack.add_argument("-o", "--output", required=True, help="Output .zip path")
    pack.add_argument("--label", default="", help="Optional label stored in metadata")

    unpack = sub.add_parser("unpack", help="Restore env files from an archive")
    unpack.add_argument("archive", help="Path to the .zip archive")
    unpack.add_argument("-d", "--destination", default=".", help="Directory to restore into")

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "pack":
        result = archive(args.files, args.output, label=args.label)
        print(result.summary())
        return 0 if result.ok else 1

    if args.command == "unpack":
        result = restore(args.archive, args.destination)
        print(result.summary())
        return 0 if result.ok else 1

    return 1  # unreachable


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
