import json
import sys
import threading
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import List


class CommitMessageEngine(ABC):
    name: str  # 표시용 이름
    PROMPT_PATH = Path("prompts/commit_message.md")
    MAX_DIFF_CHARS = 12000

    # ---------- core ----------
    @abstractmethod
    def _generate(self, diff: str) -> str:
        """
        diff를 받아 커밋 메시지 후보 리스트 반환
        """
        raise NotImplementedError

    def generate(self, diff: str) -> List[str]:
        """
        공통 진입점 (spinner 포함)
        """
        with self.spinner(f"🔮 {self.name}로 커밋 메시지 생성 중"):
            result = self._generate(diff)
            return self._parse_json(result)

    # ---------- prompt ----------
    @classmethod
    def _load_prompt(cls) -> str:
        if not cls.PROMPT_PATH.exists():
            raise RuntimeError(
                f"커밋 메시지 프롬프트 파일이 없습니다: {cls.PROMPT_PATH}\n"
            )

        return cls.PROMPT_PATH.read_text(encoding="utf-8").strip()

    def get_prompt(self, diff: str) -> str:
        """
        커밋 메시지 생성 프롬프트 (공통)
        """
        prompt = self._load_prompt()
        _diff = diff[: self.MAX_DIFF_CHARS]
        return f"{prompt}\n\n```diff\n{_diff}\n```"

    # ---------- json parsing ----------
    def _parse_json(self, text: str) -> List[str]:
        """
        LLM 응답에서 JSON 배열을 안전하게 파싱
        """
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("["), text.rfind("]")
            if start == -1 or end == -1 or end <= start:
                raise RuntimeError(f"{self.name} JSON 파싱 실패:\n{text}")
            data = json.loads(text[start : end + 1])

        if not isinstance(data, list):
            raise RuntimeError(f"{self.name} 응답이 JSON 배열이 아님:\n{data}")

        cleaned = [str(m).strip() for m in data if str(m).strip()]
        if not cleaned:
            raise RuntimeError(f"{self.name} 응답에 유효한 메시지가 없음")

        return cleaned[:10]

    # ---------- spinner ----------
    @contextmanager
    def spinner(self, message: str):
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._spinner_loop,
            args=(stop_event, message),
            daemon=True,
        )
        thread.start()
        try:
            yield
        finally:
            stop_event.set()
            thread.join(timeout=0.5)

    @staticmethod
    def _spinner_loop(stop_event: threading.Event, message: str):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not stop_event.is_set():
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r{message} {frame}   ")
            sys.stdout.flush()
            i += 1
            time.sleep(0.2)

        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
        sys.stdout.flush()
