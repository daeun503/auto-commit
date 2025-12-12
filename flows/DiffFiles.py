from dataclasses import dataclass
from typing import List


@dataclass
class DiffFiles:
    included: List[str]
    excluded: List[str]
    filtered_diff: str
