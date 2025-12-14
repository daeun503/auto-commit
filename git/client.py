import subprocess
from dataclasses import dataclass
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

    def commit(self, message: str, extra_args: List[str] | None = None) -> int:
        if not message.strip():
            raise RuntimeError("빈 커밋 메시지는 사용할 수 없습니다.")

        extra_args = extra_args or []
        cmd = ["git", "commit", "-m", message] + extra_args
        result = subprocess.run(cmd)
        return result.returncode
