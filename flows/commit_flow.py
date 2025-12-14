from dataclasses import dataclass
from typing import List

from InquirerPy import inquirer

from engines.base import CommitMessageEngine
from flows.diff_console import DiffConsole
from flows.diff_processor import DiffProcessor
from git.client import GitClient

__all__ = [
    "CommitFlow",
]


@dataclass
class CommitFlow:
    engine: CommitMessageEngine
    git: GitClient

    diff_processor: DiffProcessor
    console: DiffConsole

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
        self.console.print_selected_message(message)
        return bool(
            inquirer.confirm(
                message="이 메시지로 커밋할까요?",
                default=True,
            ).execute()
        )

    # ---------- public flow ----------
    def run(self, extra_args: List[str]) -> int:
        raw_diff = self.git.get_staged_diff()

        diff_files = self.diff_processor.process(raw_diff)
        self.console.print_diff_files(diff_files)

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
