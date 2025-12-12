import re
from dataclasses import dataclass
from typing import List

from InquirerPy import inquirer

from flows.DiffFiles import DiffFiles
from git.client import GitClient
from engines.base import CommitMessageEngine


@dataclass
class CommitFlow:
    engine: CommitMessageEngine
    git: GitClient

    # ---------- diff filtering ----------
    MAX_DIFF_CHARS = 12_000
    EXCLUDE_FILES = {
        ".gitignore",
        "poetry.lock",
        "Pipfile.lock",
        "package-lock.json",
        "yarn.lock",
    }
    EXCLUDE_SUFFIXES = {
        ".lock",
        ".min.js",
        ".map",
    }
    EXCLUDE_DIRS = {
        "node_modules/",
        "dist/",
        "build/",
        ".venv/",
        "__pycache__/",
    }

    def _filter_diff_files(self, diff: str) -> DiffFiles:
        """
        diff를 파일 단위로 분리하여 LLM에 불필요한 변경을 제거
        """
        blocks = diff.split("\ndiff --git ")
        kept: List[str] = []

        included_files = []
        excluded_files = []

        for i, block in enumerate(blocks):
            if i == 0:
                body = block
            else:
                body = "diff --git " + block

            file_path = self._extract_file_path(body)

            if self._should_exclude_block(body):
                if file_path:
                    excluded_files.append(file_path)
                continue
            else:
                if file_path:
                    included_files.append(file_path)

            kept.append(body)

        filtered = "\n".join(kept).strip()

        # 안전장치: 너무 길면 MAX_DIFF_CHARS 만큼 자름
        if len(filtered) > self.MAX_DIFF_CHARS:
            filtered = filtered[: self.MAX_DIFF_CHARS] + "\n# ... diff truncated"

        return DiffFiles(
            included=sorted(set(included_files)),
            excluded=sorted(set(excluded_files)),
            filtered_diff=filtered,
        )

    def _extract_file_path(self, block: str) -> str | None:
        """
        diff --git a/foo b/foo 에서 foo 추출
        """
        m = re.search(r"diff --git a/(.*?) b/", block)
        return m.group(1) if m else None

    def _should_exclude_block(self, block: str) -> bool:
        """
        diff 블록 하나가 제외 대상인지 판단
        """
        # 파일명 기준 제외
        for name in self.EXCLUDE_FILES:
            if f" {name}" in block:
                return True

        # suffix 기준 제외
        for suffix in self.EXCLUDE_SUFFIXES:
            if block.strip().endswith(suffix):
                return True

        # 디렉토리 기준 제외
        for d in self.EXCLUDE_DIRS:
            if f" a/{d}" in block or f" b/{d}" in block:
                return True

        return False

    def print_diff_files(self, files: DiffFiles) -> None:
        print()
        print("📦 커밋 대상 파일 (LLM 전달됨)")

        if not files.included:
            print("  (없음)")
        else:
            for f in files.included:
                print(f"  📄 {f}")

        if files.excluded:
            print()
            print("🚫 제외된 파일")
            for f in files.excluded:
                # ANSI dim (회색)
                print(f"\033[90m  ░░ {f}\033[0m")

        print()

    # ---------- UI ----------
    def select_message(self, candidates: List[str]) -> str:
        choices = candidates + ["✏️ 직접 입력 (내가 쓰기)"]
        answer = inquirer.select(
            message="커밋 메시지를 선택하세요:",
            choices=choices,
            default=choices[0],
        ).execute()

        initial = "" if answer == "✏️ 직접 입력 (내가 쓰기)" else str(answer).strip()

        edited = inquirer.text(
            message="커밋 메시지를 수정/확정하세요:",
            default=initial,
        ).execute()

        return (edited or "").strip()

    def confirm_commit(self, message: str) -> bool:
        print()
        print("선택된 커밋 메시지:")
        print(f"  {message}")
        print()

        return bool(
            inquirer.confirm(
                message="이 메시지로 커밋할까요?",
                default=True,
            ).execute()
        )

    # ---------- public flow ----------
    def run(self, extra_args: List[str]) -> int:
        raw_diff = self.git.get_staged_diff()

        diff_files = self._filter_diff_files(raw_diff)
        self.print_diff_files(diff_files)

        diff = diff_files.filtered_diff.strip()
        if not diff:
            raise RuntimeError(
                "LLM에 전달할 유효한 diff가 없습니다. 모든 변경사항이 제외 대상 파일일 수 있습니다"
            )

        suggestions = self.engine.generate(diff)
        chosen = self.select_message(suggestions)

        if not chosen:
            print("  ❌ 커밋이 취소되었습니다.")
            return 0

        if not self.confirm_commit(chosen):
            print("  ❌ 커밋이 취소되었습니다.")
            return 0

        return self.git.commit(chosen, extra_args)
