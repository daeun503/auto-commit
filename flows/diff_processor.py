import re
from typing import List

from constants import Constants
from flows.dtos import DiffFiles, DiffProcessConfig

__all__ = [
    "DiffProcessor",
]


class DiffProcessor:
    """
    staged diff 문자열을 받아서:
    1. 파일 단위로 분해
    2. file_path 기준으로 diff 제외 규칙 적용
    3. LLM 전달용 diff 생성
    4. included / excluded 파일 목록 생성
    """

    def __init__(self):
        self.config = DiffProcessConfig(
            max_diff_chars=Constants.MAX_DIFF_CHARS,
            exclude_files=Constants.ExcludeRules.FILES,
            exclude_suffixes=Constants.ExcludeRules.SUFFIXES,
            exclude_dirs=Constants.ExcludeRules.DIRS,
        )

    def process(self, diff: str) -> DiffFiles:
        blocks = diff.split("\ndiff --git ")
        kept: List[str] = []
        included_files: List[str] = []
        excluded_files: List[str] = []

        for i, block in enumerate(blocks):
            body = block if i == 0 else "diff --git " + block

            file_path = self._extract_file_path(body)
            if not file_path:
                continue

            if self._should_exclude_file(file_path):
                excluded_files.append(file_path)
                continue

            included_files.append(file_path)
            kept.append(body)

        filtered = "\n".join(kept).strip()
        if len(filtered) > self.config.max_diff_chars:
            filtered = filtered[: self.config.max_diff_chars] + "\n# ... diff truncated"

        return DiffFiles(
            included=sorted(set(included_files)),
            excluded=sorted(set(excluded_files)),
            filtered_diff=filtered,
        )

    def _extract_file_path(self, block: str) -> str | None:
        """
        diff --git a/foo b/foo 에서 b쪽 경로 우선 추출
        """
        m = re.search(r"^diff --git a/(.+?) b/(.+?)\n", block, re.MULTILINE)
        return m.group(2) if m else None

    def _should_exclude_file(self, file_path: str) -> bool:
        """
        file_path 기준 제외 판단
        """
        path = file_path.replace("\\", "/")
        filename = path.rsplit("/", 1)[-1]

        if filename in self.config.exclude_files:
            return True

        for suffix in self.config.exclude_suffixes:
            if path.endswith(suffix):
                return True

        for d in self.config.exclude_dirs:
            if path.startswith(d) or f"/{d}" in path:
                return True

        return False
