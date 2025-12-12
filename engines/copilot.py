import shutil
import subprocess

from .base import CommitMessageEngine


class CopilotEngine(CommitMessageEngine):
    name = "Copilot"

    @staticmethod
    def _ensure_copilot_available() -> None:
        if shutil.which("copilot") is None:
            raise RuntimeError(
                "copilot CLI가 설치되어 있지 않습니다.\n설치 방법: brew install copilot"
            )

    def _generate(self, diff: str) -> str:
        self._ensure_copilot_available()

        prompt = self.get_prompt(diff)
        try:
            result = subprocess.run(
                ["copilot", "-p", prompt],
                capture_output=True,
                text=True,
            )
        except Exception as e:
            raise RuntimeError(f"Copilot CLI 실행 실패: {e}") from e

        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()

        if result.returncode != 0:
            # 인증 관련 힌트
            if "authentication" in err.lower() or "login" in err.lower():
                raise RuntimeError(
                    "Copilot 인증 정보가 없습니다.\n"
                    "shell에서 `copilot login` 명령어를 실행하여 로그인하세요.\n\n"
                )
            raise RuntimeError(f"Copilot CLI 오류:\n{err or out}")

        if not out:
            raise RuntimeError("Copilot 응답이 비어 있습니다.")

        return out
