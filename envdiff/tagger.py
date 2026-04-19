"""Tag env keys with user-defined labels based on pattern rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Set


@dataclass
class TagResult:
    tags: Dict[str, Set[str]] = field(default_factory=dict)  # key -> set of tags
    rules: int = 0

    def keys_for_tag(self, tag: str) -> List[str]:
        return sorted(k for k, ts in self.tags.items() if tag in ts)

    def tags_for_key(self, key: str) -> Set[str]:
        return self.tags.get(key, set())

    def summary(self) -> str:
        total = sum(len(ts) for ts in self.tags.values())
        return f"{len(self.tags)} keys tagged, {total} total tag assignments, {self.rules} rules applied"


def tag(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
) -> TagResult:
    """Apply tagging rules to env keys.

    Args:
        env: parsed env dict
        rules: mapping of tag -> list of glob patterns
    """
    result: Dict[str, Set[str]] = {k: set() for k in env}
    for tag_name, patterns in rules.items():
        for key in env:
            for pat in patterns:
                if fnmatch(key, pat):
                    result[key].add(tag_name)
                    break
    # Remove keys with no tags
    tagged = {k: v for k, v in result.items() if v}
    return TagResult(tags=tagged, rules=len(rules))


def tag_from_presets(
    env: Dict[str, str],
    extra_rules: Dict[str, List[str]] | None = None,
) -> TagResult:
    """Tag using built-in presets plus optional extra rules."""
    presets: Dict[str, List[str]] = {
        "secret": ["*SECRET*", "*PASSWORD*", "*TOKEN*", "*KEY*", "*PRIVATE*"],
        "url": ["*URL*", "*HOST*", "*ENDPOINT*"],
        "debug": ["*DEBUG*", "*VERBOSE*", "*LOG*"],
        "database": ["*DB_*", "*DATABASE*", "*POSTGRES*", "*MYSQL*"],
    }
    if extra_rules:
        for t, patterns in extra_rules.items():
            presets.setdefault(t, []).extend(patterns)
    return tag(env, presets)
