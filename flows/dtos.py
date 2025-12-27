from dataclasses import dataclass, field
from typing import List, Set

__all__ = [
    "DiffProcessConfig",
    "DiffFiles",
]


@dataclass(frozen=True)
class DiffProcessConfig:
    max_diff_chars: int
    exclude_files: Set[str]
    exclude_suffixes: Set[str]
    exclude_dirs: Set[str]


@dataclass
class DiffFiles:
    included: List[str]
    excluded: List[str]
    filtered_diff: str
