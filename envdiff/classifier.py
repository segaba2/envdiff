"""Classify env keys into semantic categories based on naming patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# (category, compiled pattern)
_RULES: List[tuple[str, re.Pattern[str]]] = [
    ("secret",  re.compile(r"(SECRET|PASSWORD|PASSWD|TOKEN|API_KEY|PRIVATE|CREDENTIALS)", re.I)),
    ("url",     re.compile(r"(URL|URI|ENDPOINT|HOST|DOMAIN)", re.I)),
    ("database",re.compile(r"(DB_|DATABASE|POSTGRES|MYSQL|MONGO|REDIS|SQLITE)", re.I)),
    ("port",    re.compile(r"PORT$", re.I)),
    ("flag",    re.compile(r"(ENABLE|DISABLE|FLAG|FEATURE|DEBUG|VERBOSE)", re.I)),
    ("path",    re.compile(r"(PATH|DIR|DIRECTORY|FILE|ROOT)", re.I)),
    ("email",   re.compile(r"(EMAIL|MAIL)", re.I)),
    ("timeout", re.compile(r"(TIMEOUT|TTL|EXPIRY|EXPIRATION)", re.I)),
]

_FALLBACK = "general"


@dataclass
class ClassifyResult:
    categories: Dict[str, str] = field(default_factory=dict)   # key -> category
    by_category: Dict[str, List[str]] = field(default_factory=dict)  # category -> [keys]

    def summary(self) -> str:
        parts = [f"{cat}: {len(keys)}" for cat, keys in sorted(self.by_category.items())]
        return "Categories — " + ", ".join(parts) if parts else "No keys classified."


def _classify_key(key: str) -> str:
    """Return the first matching category for *key*, or 'general'."""
    for category, pattern in _RULES:
        if pattern.search(key):
            return category
    return _FALLBACK


def classify(env: Dict[str, str]) -> ClassifyResult:
    """Classify every key in *env* and return a :class:`ClassifyResult`."""
    categories: Dict[str, str] = {}
    by_category: Dict[str, List[str]] = {}

    for key in env:
        cat = _classify_key(key)
        categories[key] = cat
        by_category.setdefault(cat, []).append(key)

    # sort keys within each category for deterministic output
    for cat in by_category:
        by_category[cat].sort()

    return ClassifyResult(categories=categories, by_category=by_category)
