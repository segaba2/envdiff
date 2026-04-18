"""High-level diff orchestration: parse, filter, sort, and compare env files."""
from pathlib import Path
from typing import Optional, List

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.filter import filter_keys, filter_prefix
from envdiff.sorter import sort_keys


def diff_files(
    path_a: str,
    path_b: str,
    exclude_patterns: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    sort: str = "alpha",
) -> "DiffResult":  # noqa: F821
    """Parse two .env files and return a DiffResult.

    Args:
        path_a: Path to the first .env file.
        path_b: Path to the second .env file.
        exclude_patterns: Optional glob/regex patterns to exclude keys.
        prefix: If set, only keys starting with this prefix are compared.
        sort: Sort strategy passed to sort_keys ('alpha' or 'status').

    Returns:
        A DiffResult describing missing and mismatched keys.
    """
    env_a = parse_env_file(Path(path_a))
    env_b = parse_env_file(Path(path_b))

    if prefix:
        env_a = filter_prefix(env_a, prefix)
        env_b = filter_prefix(env_b, prefix)

    if exclude_patterns:
        env_a = filter_keys(env_a, exclude_patterns)
        env_b = filter_keys(env_b, exclude_patterns)

    result = compare(env_a, env_b)
    result = sort_keys(result, strategy=sort)
    return result
