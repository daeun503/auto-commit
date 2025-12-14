from dataclasses import dataclass, field
from typing import List, Set

__all__ = [
    "DiffProcessConfig",
    "DiffFiles",
]


@dataclass(frozen=True)
class DiffProcessConfig:
    max_diff_chars: int = 12_000
    exclude_files: Set[str] = field(default_factory=set)
    exclude_suffixes: Set[str] = field(default_factory=set)
    exclude_dirs: Set[str] = field(default_factory=set)


@dataclass
class DiffFiles:
    included: List[str]
    excluded: List[str]
    filtered_diff: str
