import json

import requests
from pathlib import Path

from .base import CommitMessageEngine


class OllamaEngine(CommitMessageEngine):
    name = "Ollama"
    MODEL_PATH = Path("config/ollama_model.txt")

    @classmethod
    def _load_model(cls) -> str:
        if not cls.MODEL_PATH.exists():
            raise RuntimeError(f"Ollama 모델 설정 파일이 없습니다: {cls.MODEL_PATH}\n")

        model = cls.MODEL_PATH.read_text(encoding="utf-8").strip()
        if not model:
            raise RuntimeError(
                f"Ollama 모델 설정 파일이 비어 있습니다: {cls.MODEL_PATH}\n"
            )

        return model

    def _generate(self, diff: str) -> str:
        prompt = self.get_prompt(diff)
        model = self._load_model()

        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": 128,
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
                timeout=300,
            )
        except requests.RequestException as e:
            raise RuntimeError(
                "Ollama 서버에 연결할 수 없습니다.\n"
                "Ollama가 실행 중인지 확인하세요 (ollama serve)."
            ) from e

        if resp.status_code != 200:
            raise RuntimeError(
                f"Ollama API 호출 실패 (HTTP {resp.status_code}):\n{resp.text}"
            )

        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise RuntimeError(f"Ollama 응답이 JSON이 아닙니다:\n{resp.text}")

        if "error" in data:
            raise RuntimeError(
                f"Ollama 오류: {data['error']}\n"
                f"모델이 설치되어 있는지 확인하세요:\n"
                f"  ollama pull {model}"
            )

        out = (data.get("response") or "").strip()
        if not out:
            raise RuntimeError("Ollama 응답이 비어 있습니다.")

        return out
