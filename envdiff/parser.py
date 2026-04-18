"""Parser for .env files."""

from pathlib import Path
from typing import Dict, Optional


class EnvParseError(Exception):
    """Raised when a .env file cannot be parsed."""
    pass


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dictionary of key-value pairs.

    - Ignores blank lines and lines starting with '#'.
    - Supports keys without values (e.g. 'MY_KEY' or 'MY_KEY=').
    - Strips surrounding quotes from values.

    Args:
        filepath: Path to the .env file.

    Returns:
        Dict mapping variable names to their values (or None if no value set).

    Raises:
        EnvParseError: If the file cannot be read or a line is malformed.
    """
    path = Path(filepath)
    if not path.exists():
        raise EnvParseError(f"File not found: {filepath}")

    env: Dict[str, Optional[str]] = {}

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EnvParseError(f"Cannot read file {filepath}: {exc}") from exc

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # Skip blanks and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            # Treat as a key with no value
            key = line
            if not _valid_key(key):
                raise EnvParseError(f"Invalid key '{key}' at line {lineno} in {filepath}")
            env[key] = None
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not _valid_key(key):
            raise EnvParseError(f"Invalid key '{key}' at line {lineno} in {filepath}")

        # Strip matching surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]

        env[key] = value if value != "" else None

    return env


def _valid_key(key: str) -> bool:
    """Return True if key is a valid environment variable name."""
    return bool(key) and all(c.isalnum() or c == "_" for c in key)
