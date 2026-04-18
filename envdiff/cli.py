"""CLI entry point for envdiff."""

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and flag missing or mismatched keys.",
    )
    p.add_argument("file_a", type=Path, help="First .env file")
    p.add_argument("file_b", type=Path, help="Second .env file")
    p.add_argument(
        "--no-values",
        action="store_true",
        help="Hide actual values in mismatch output",
    )
    return p


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for path in (args.file_a, args.file_b):
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(env_a, env_b)

    label_a = args.file_a.name
    label_b = args.file_b.name

    if args.no_values and result.mismatched:
        for key in sorted(result.mismatched):
            result.mismatched[key] = ("***", "***")

    print(result.summary(label_a=label_a, label_b=label_b))
    return 1 if result.has_diff else 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
