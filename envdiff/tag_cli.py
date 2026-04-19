"""CLI for tagging env file keys by pattern rules."""
from __future__ import annotations
import argparse
import json
import sys
from envdiff.parser import parse_env_file
from envdiff.tagger import tag_from_presets


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-tag",
        description="Tag keys in a .env file using built-in and custom rules.",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--tag",
        dest="filter_tag",
        metavar="TAG",
        help="Only show keys with this tag",
    )
    return p


def run(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = tag_from_presets(env)

    if args.filter_tag:
        keys = result.keys_for_tag(args.filter_tag)
        data = {k: sorted(result.tags_for_key(k)) for k in keys}
    else:
        data = {k: sorted(v) for k, v in result.tags.items()}

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        if not data:
            print("No tagged keys found.")
        else:
            for key, tags in sorted(data.items()):
                print(f"{key}: {', '.join(tags)}")
        print()
        print(result.summary())

    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
