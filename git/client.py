import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class GitClient:
    def has_staged_changes(self) -> bool:
        # 변경이 없으면 returncode 0
        # 변경이 있으면 returncode 1
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        return result.returncode != 0

    def get_staged_diff(self) -> str:
        if not self.has_staged_changes():
            raise RuntimeError(
                "staged 된 변경사항이 없습니다. 먼저 'git add' 를 해주세요."
            )

        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git diff --cached 실행 실패:\n{result.stderr}")

        diff = (result.stdout or "").strip()
        if not diff:
            raise RuntimeError("staged 된 diff 내용을 읽지 못했습니다.")
        return diff

    def get_current_branch(self, pwd: Path) -> str:
        result = subprocess.run(
            ["git", "-C", str(pwd), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"현재 브랜치 이름을 가져오지 못했습니다:\n{result.stderr}"
            )

        branch = result.stdout
        if not branch:
            raise RuntimeError("현재 브랜치 이름이 비어 있습니다.")
        if branch == "HEAD":
            raise RuntimeError("detached HEAD 상태입니다.")

        return branch.strip()

    def commit(self, message: str, extra_args: List[str] | None = None) -> int:
        if not message.strip():
            raise RuntimeError("빈 커밋 메시지는 사용할 수 없습니다.")

        extra_args = extra_args or []
        cmd = ["git", "commit", "-m", message] + extra_args
        result = subprocess.run(cmd)
        return result.returncode
