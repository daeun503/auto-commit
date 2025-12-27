from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml
from InquirerPy import inquirer

from constants import Constants
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

    GITMOJI_PATH = Constants.Paths.GITMOJI_PATH

    def _load_gitmoji(self):
        path = Path(self.GITMOJI_PATH)
        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        if not isinstance(raw, dict):
            return {}

        return {
            str(k): str(v)
            for k, v in raw.items()
            if isinstance(k, str) and isinstance(v, str)
        }

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

    def edit_gitmoji_prefix(self, message: str) -> str:
        gitmoji = self._load_gitmoji()
        if not gitmoji:
            return message

        choices = ["❌ 수정하지 않음"] + [
            f"{v} {prefix}" for prefix, v in gitmoji.items()
        ]
        answer = inquirer.select(
            message="현재 커밋 메시지의 gitmoji와 prefix를 수정할까요?",
            choices=choices,
            default=choices[0],
        ).execute()

        if answer == "❌ 수정하지 않음":
            return message

        # [TEST] ✨ feat: add login => ]를 기준으로 메타정보 분리
        meta = ""
        if message.startswith("[") and "]" in message:
            meta, message = message.split("]", 1)
            message = message.lstrip()
            meta += "]"

        # ✨ feat: add login => :를 기준으로 분리
        body = message
        if ":" in message:
            _, body = message.split(":", 1)
            body = body.lstrip()

        meta_part = f"{meta} " if meta else ""
        return f"{meta_part}{answer}: {body}".strip()

    def confirm_commit(self, message: str) -> bool:
        self.console.print_selected_message(message)
        return bool(
            inquirer.confirm(
                message="이 메시지로 커밋할까요?",
                default=True,
            ).execute()
        )

    # ---------- public flow ----------
    def run(self, use_branch_prefix: bool, extra_args: List[str]) -> int:
        raw_diff = self.git.get_staged_diff()

        diff_files = self.diff_processor.process(raw_diff)
        self.console.print_diff_files(diff_files)

        diff = diff_files.filtered_diff.strip()
        if not diff:
            raise RuntimeError(
                "LLM에 전달할 유효한 diff가 없습니다. 모든 변경사항이 제외 대상 파일일 수 있습니다"
            )

        suggestions = self.engine.generate(diff)

        if use_branch_prefix:
            branch = self.git.get_current_branch(Path.cwd())
            chosen = self.select_message([f"[{branch}] {s}" for s in suggestions])
        else:
            chosen = self.select_message(suggestions)

        edited = self.edit_gitmoji_prefix(chosen)
        if not edited:
            print("  ❌ 커밋이 취소되었습니다.")
            return 0

        if not self.confirm_commit(edited):
            print("  ❌ 커밋이 취소되었습니다.")
            return 0

        return self.git.commit(edited, extra_args)
